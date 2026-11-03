#!/usr/bin/env python3
"""Hooks analyzer: measure every frame of a short video and lay out the
frames a reviewer has to look at.

    python analyze.py video.mp4 --out review/
    python analyze.py video.mp4 --out review/ --transcript captions.srt
    python analyze.py video.mp4 --out review/ --span 12.0-14.5   # every frame in a window

Needs ffmpeg and ffprobe 6.0+ on PATH. Python standard library only.

Writes, inside --out:
  report.md      measured facts and auto-flags. Read this first.
  report.json    the same data for tools
  frames.csv     one row per decoded frame (scene change, brightness, motion, crop)
  seconds.csv    one row per second (cuts, motion, loudness, words)
  frames/        first and last frame at full size, plus test views of the first frame
  sheets/        labelled contact sheets: hook, cuts, timeline, tail, loop seam, spans

The machine pass finds candidates. A person or agent still has to look at the
sheets and confirm each flag; see SKILL.md.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import json
import math
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import readability as rd  # noqa: E402

# Thresholds. Each is a Hooks default, not a platform rule; tune per channel.
T = {
    "cut_scene": 0.30,       # ffmpeg scene score that counts as a hard cut
    "jump_scene": 0.012,     # smallest one-frame spike that counts as a jump (hidden join, jump cut)
    "grad_low": 0.05,        # per-frame change that may be part of a dissolve or fade
    "grad_min_frames": 5,    # a gradual change must last at least this many frames
    "black_yavg": 22.0,      # mean luma below this is a black frame (video black is 16)
    "flash_frames": 2,       # a shot this short (in frames) is a flash frame
    "static_ydif": 0.8,      # mean luma change per frame below this means nothing moves
    "static_secs": 2.0,
    "change_thr": 15.0,      # thumbnail difference over 0.5 s that counts as a visual change
    "hold_minor": 5.0,       # seconds without a cut or visual change
    "hold_major": 8.0,
    "freeze_minor": 1.0,     # frozen picture, seconds (short holds on text are normal)
    "freeze_major": 2.0,
    "hook_window": 3.0,
    "audio_onset": 0.5,
    "word_onset": 0.6,
    "gap_secs": 0.35,
    "long_gap_secs": 0.8,
    "tail_secs": 0.5,
    "letterbox_frac": 0.90,  # picture area narrower than this share of the frame = bars
    "lufs_low": -18.0,
    "lufs_high": -10.0,
    "true_peak": -1.0,
    "dark_hook_yavg": 45.0,
    "target_seconds": 33.5,  # Jenny Hoyos's reported sweet spot; a heuristic to test
    "target_band": 2.5,
}
PROXY_W = 360   # analysis proxy width
TILE_W = 270    # contact-sheet tile width
THUMB_W, THUMB_H = 32, 56  # grey thumbnails for the visual-change signal
SEV_ORDER = {"BLOCKER": 0, "MAJOR": 1, "MINOR": 2, "INFO": 3}

FONT_CANDIDATES = [
    "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


# ---------------------------------------------------------------- helpers

def run(cmd, cwd=None, check=True):
    p = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(map(str, cmd))}\n{p.stderr[-3000:]}")
    return p


def esc(path) -> str:
    """Escape a path for use inside a quoted ffmpeg filter option."""
    return str(path).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def find_font(user_font: str | None) -> str | None:
    for f in ([user_font] if user_font else []) + FONT_CANDIDATES:
        if f and Path(f).is_file():
            return f
    return None


def fmt_t(t: float) -> str:
    return f"{t:5.2f}s"


def ratio(s: str) -> float:
    try:
        n, d = s.split("/")
        return float(n) / float(d) if float(d) else 0.0
    except (ValueError, ZeroDivisionError):
        return 0.0


# ---------------------------------------------------------------- probing

def probe(video: Path) -> dict:
    p = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", video])
    info = json.loads(p.stdout)
    streams = info.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"
              and not s.get("disposition", {}).get("attached_pic")), None)
    if not v:
        sys.exit("hooks: no video stream found")
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list") or []:
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    if v.get("tags", {}).get("rotate"):
        rot = int(v["tags"]["rotate"])
    if abs(rot) % 180 == 90:  # ffmpeg auto-rotates on decode, so report display size
        w, h = h, w
    fps = ratio(v.get("avg_frame_rate", "0/0")) or ratio(v.get("r_frame_rate", "0/0"))
    dur = float(info.get("format", {}).get("duration") or v.get("duration") or 0)
    return {
        "width": w, "height": h, "rotation": rot, "fps": round(fps, 3), "duration": round(dur, 3),
        "video_codec": v.get("codec_name"), "has_audio": a is not None,
        "audio_codec": a.get("codec_name") if a else None,
        "subtitle_streams": sum(1 for s in streams if s.get("codec_type") == "subtitle"),
        "bitrate_kbps": round(int(info.get("format", {}).get("bit_rate", 0) or 0) / 1000),
    }


# ---------------------------------------------------------------- per-frame pass

def frame_pass(video: Path, work: Path) -> tuple[list[dict], list, list, list[bytes]]:
    """One decode: per-frame metadata to a file, tiny grey thumbnails to stdout."""
    graph = (f"[0:v:0]setpts=PTS-STARTPTS,split=2[a][b];"
             f"[a]scale={PROXY_W}:-2:flags=area,select='gte(scene\\,0)',signalstats,"
             "cropdetect=limit=24:round=2:reset=1,blackdetect=d=0.04:pix_th=0.10,"
             "freezedetect=n=-60dB:d=0.5,metadata=mode=print:file=frames_meta.txt[m];"
             f"[b]scale={THUMB_W}:{THUMB_H}:flags=area,format=gray[t]")
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-filter_complex", graph,
           "-map", "[m]", "-f", "null", "null", "-map", "[t]", "-f", "rawvideo", "-"]
    proc = subprocess.run(cmd, cwd=work, capture_output=True)
    stderr = proc.stderr.decode("utf-8", "replace")
    if proc.returncode != 0:
        raise RuntimeError(f"frame pass failed:\n{stderr[-3000:]}")
    size = THUMB_W * THUMB_H
    thumbs = [proc.stdout[k:k + size] for k in range(0, len(proc.stdout) - size + 1, size)]
    frames, cur = [], None
    keys = {"lavfi.scene_score": "scene", "lavfi.signalstats.YAVG": "yavg",
            "lavfi.signalstats.SATAVG": "sat", "lavfi.signalstats.YDIF": "ydif",
            "lavfi.cropdetect.w": "crop_w", "lavfi.cropdetect.h": "crop_h"}
    with open(work / "frames_meta.txt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            m = re.match(r"frame:(\d+)\s+pts:\S+\s+pts_time:(\S+)", line)
            if m:
                try:
                    t = float(m[2])
                except ValueError:
                    t = frames[-1]["t"] if frames else 0.0
                cur = {"n": int(m[1]), "t": t, "scene": 0.0, "yavg": 0.0, "sat": 0.0, "ydif": 0.0,
                       "crop_w": None, "crop_h": None}
                frames.append(cur)
            elif cur is not None and "=" in line:
                k, val = line.split("=", 1)
                if k in keys:
                    try:
                        cur[keys[k]] = float(val)
                    except ValueError:
                        pass
    (work / "frames_meta.txt").unlink(missing_ok=True)
    if frames:
        frames[0]["scene"] = 0.0
        frames[0]["ydif"] = 0.0
    err = stderr
    blacks = [(float(a), float(b)) for a, b in
              re.findall(r"black_start:\s*([-\d.]+)\s+black_end:\s*([-\d.]+)", err)]
    fs = [float(x) for x in re.findall(r"freeze_start:\s*([-\d.]+)", err)]
    fe = [float(x) for x in re.findall(r"freeze_end:\s*([-\d.]+)", err)]
    end_t = frames[-1]["t"] if frames else 0.0
    freezes = [(s, fe[i] if i < len(fe) else end_t) for i, s in enumerate(fs)]
    return frames, blacks, freezes, thumbs


def visual_change(thumbs: list[bytes], fps: float) -> list[float]:
    """Mean grey-level difference between each frame and the frame 0.5 s earlier.

    Unlike the cut detector this sees animated transitions and layout changes, so it
    measures how often the picture actually changes. Talking heads stay under ~10;
    cuts and real scene changes go well above T["change_thr"].
    """
    lag = max(1, round(0.5 * fps))
    out = [0.0] * len(thumbs)
    for i in range(lag, len(thumbs)):
        a, b = thumbs[i], thumbs[i - lag]
        out[i] = sum(abs(x - y) for x, y in zip(a, b)) / max(len(a), 1)
    return out


# ---------------------------------------------------------------- audio pass

def audio_pass(video: Path, work: Path, duration: float) -> dict:
    p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-map", "0:a:0", "-vn", "-sn",
             "-af", "ebur128=peak=true:framelog=info,silencedetect=n=-35dB:d=0.25",
             "-f", "null", "-"], cwd=work, check=False)
    err = p.stderr
    mom = []
    for t, mv in re.findall(r"\bt:\s*([\d.]+)\s+TARGET:\S+\s+LUFS\s+M:\s*(-?inf|-?[\d.]+|nan)", err):
        try:
            mom.append((float(t), max(float(mv), -70.0)))
        except ValueError:
            mom.append((float(t), -70.0))
    summ = err[err.rfind("Summary:"):] if "Summary:" in err else ""

    def grab(pat):
        m = re.search(pat, summ, re.S)
        if not m:
            return None
        try:
            return float(m[1])
        except ValueError:
            return None

    starts = [float(x) for x in re.findall(r"silence_start:\s*([-\d.e]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([-\d.e]+)", err)]
    silences = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else duration
        silences.append((max(0.0, s), min(e, duration)))
    onset = 0.0
    if silences and silences[0][0] <= 0.05:
        onset = silences[0][1]
    tail = 0.0
    if silences and silences[-1][1] >= duration - 0.06:
        tail = duration - silences[-1][0]
    gaps = [(s, e) for s, e in silences if s > 0.05 and e < duration - 0.06]
    return {
        "integrated_lufs": grab(r"I:\s+(-?[\d.]+)\s+LUFS"),
        "lra_lu": grab(r"LRA:\s+([\d.]+)\s+LU"),
        "true_peak_dbtp": grab(r"Peak:\s+(-?[\d.]+|-inf)\s+dBFS"),
        "silences": [(round(s, 3), round(e, 3)) for s, e in silences],
        "onset": round(onset, 3), "tail_silence": round(tail, 3),
        "gaps": [(round(s, 3), round(e, 3)) for s, e in gaps],
        "momentary": mom,
    }


# ---------------------------------------------------------------- transcripts

_TS = r"(?:(\d+):)?(\d{1,2}):(\d{2})[,.](\d{1,3})"


def _tsec(g) -> float:
    h, m, s, ms = g
    return int(h or 0) * 3600 + int(m) * 60 + int(s) + int(ms.ljust(3, "0")) / 1000


def parse_cues(text: str) -> list[dict]:
    segs = []
    for block in re.split(r"\n\s*\n", text.replace("\r", "")):
        lines = block.strip().split("\n")
        for i, ln in enumerate(lines):
            m = re.search(_TS + r"\s*-->\s*" + _TS, ln)
            if m:
                g = m.groups()
                body = " ".join(x.strip() for x in lines[i + 1:] if x.strip())
                body = re.sub(r"<[^>]+>|\{\\[^}]*\}", "", body).strip()
                if body:
                    segs.append({"start": _tsec(g[0:4]), "end": _tsec(g[4:8]), "text": body})
                break
    return segs


def _join(tokens: list[str]) -> str:
    return " ".join(t.strip() for t in tokens if t and t.strip())


def words_to_segments(words: list[dict]) -> list[dict]:
    segs, cur = [], []

    def flush():
        if cur:
            segs.append({"start": cur[0]["start"], "end": cur[-1]["end"],
                         "text": _join([w["word"] for w in cur])})
            cur.clear()

    for w in words:
        if cur and w["start"] - cur[-1]["end"] > 0.6:
            flush()
        cur.append(w)
        if re.search(r"[.!?]$", w["word"].strip()):
            flush()
    flush()
    return segs


def _norm_items(items) -> tuple[list[dict], list[dict]]:
    segs, words = [], []
    for it in items or []:
        if not isinstance(it, dict):
            continue
        st = it.get("start", it.get("from", (it.get("offsets") or {}).get("from")))
        en = it.get("end", it.get("to", (it.get("offsets") or {}).get("to")))
        if st is None or en is None:
            continue
        if "offsets" in it:  # whisper.cpp JSON stores milliseconds
            st, en = st / 1000, en / 1000
        if "word" in it and "text" not in it:
            words.append({"start": float(st), "end": float(en), "word": str(it["word"])})
        else:
            segs.append({"start": float(st), "end": float(en), "text": str(it.get("text", "")).strip()})
            for w in it.get("words") or []:
                if isinstance(w, dict) and "start" in w:
                    words.append({"start": float(w["start"]), "end": float(w["end"]),
                                  "word": str(w.get("word", w.get("text", "")))})
    return segs, words


def load_transcript(path: Path, duration: float, offset: float = 0.0) -> dict | None:
    """Load captions or word timings. offset = where the video starts inside the transcript."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    suffix = path.suffix.lower()
    segs, words = [], []
    if suffix in (".srt", ".vtt", ".ass"):
        segs = parse_cues(raw)
    elif suffix in (".json", ".jsonl"):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = [json.loads(x) for x in raw.splitlines() if x.strip().startswith("{")]
        if isinstance(data, dict):
            for key in ("segments", "sentences", "transcription", "cues", "captions", "chunks"):
                if isinstance(data.get(key), list):
                    segs, words = _norm_items(data[key])
                    break
            if isinstance(data.get("words"), list):
                _, words = _norm_items(data["words"])
        elif isinstance(data, list):
            segs, words = _norm_items(data)
        if not segs and words:
            segs = words_to_segments(words)
        ends = [s["end"] for s in segs]
        if ends and duration and max(ends) > max(duration * 20, 1000):  # milliseconds
            segs = [{**s, "start": s["start"] / 1000, "end": s["end"] / 1000} for s in segs]
            words = [{**w, "start": w["start"] / 1000, "end": w["end"] / 1000} for w in words]
    else:
        text = raw.strip()
        return {"text": text, "segments": [], "words": [], "timed": False, "source": str(path)} if text else None

    if offset:
        segs = [{**s, "start": s["start"] - offset, "end": s["end"] - offset} for s in segs]
        words = [{**w, "start": w["start"] - offset, "end": w["end"] - offset} for w in words]
        segs = [s for s in segs if s["end"] > 0]
        words = [w for w in words if w["end"] > 0]
    full_end = max((s["end"] for s in segs), default=0.0)
    clip = duration + 0.01 if duration else float("inf")
    segs = [{**s, "end": min(s["end"], duration or s["end"])} for s in segs if s["start"] < clip and s["text"]]
    words = [{**w, "end": min(w["end"], duration or w["end"])} for w in words if w["start"] < clip]
    if not segs:
        return None
    text = _join([s["text"] for s in segs])
    return {"text": text, "segments": segs, "words": words, "timed": True, "source": str(path),
            "clipped_from": round(full_end, 2) if duration and full_end > duration + 0.5 else None}


def trim_script(script: str, spoken: str) -> str:
    """Cut a (possibly longer) script to the amount of speech in the video."""
    n = len(rd.en_words(spoken))
    ms = list(re.finditer(r"[A-Za-z0-9][A-Za-z0-9'’%.-]*", script))
    if len(ms) <= n:
        return script
    end = ms[n - 1].end()
    tail = re.match(r"[^\sA-Za-z0-9]*", script[end:])
    return script[:end + (tail.end() if tail else 0)]


def check_alignment(transcript: dict, audio: dict) -> dict:
    """How many measured silences fall where the transcript has a pause between words."""
    units = transcript["words"] or transcript["segments"]
    pauses = [(a["end"], b["start"]) for a, b in zip(units, units[1:]) if b["start"] - a["end"] >= 0.15]
    gaps = [(s, e) for s, e in audio["gaps"] if e - s >= 0.3]
    matched = 0
    for s, e in gaps:
        if any(min(e, pe) - max(s, ps) >= 0.5 * min(e - s, pe - ps) for ps, pe in pauses):
            matched += 1
    return {"gaps": len(gaps), "matched": matched}


def transcribe(video: Path, work: Path, info: dict, args) -> tuple[Path | None, str | None]:
    if info["subtitle_streams"]:
        out = work / "embedded.srt"
        p = run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", video, "-map", "0:s:0", out.name],
                cwd=work, check=False)
        if p.returncode == 0 and out.exists() and out.stat().st_size > 0:
            return out, "embedded subtitle stream"
    if args.whisper_model and info["has_audio"]:
        af = (f"whisper=model='{esc(Path(args.whisper_model).resolve())}':language=auto"
              ":queue=10:destination=asr.srt:format=srt")
        p = run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-vn", "-af", af, "-f", "null", "-"],
                cwd=work, check=False)
        if p.returncode == 0 and (work / "asr.srt").exists():
            return work / "asr.srt", "ffmpeg whisper filter"
        print("hooks: ffmpeg whisper filter failed:\n" + p.stderr[-800:], file=sys.stderr)
    if args.asr == "faster-whisper" and info["has_audio"]:
        try:
            from faster_whisper import WhisperModel  # type: ignore
        except ImportError:
            print("hooks: faster-whisper is not installed (pip install faster-whisper)", file=sys.stderr)
            return None, None
        model = WhisperModel(args.asr_model)
        segments, _ = model.transcribe(str(video), word_timestamps=True)
        data = {"segments": [{"start": s.start, "end": s.end, "text": s.text,
                              "words": [{"word": w.word, "start": w.start, "end": w.end} for w in (s.words or [])]}
                             for s in segments]}
        out = work / "asr.json"
        out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        return out, f"faster-whisper ({args.asr_model})"
    return None, None


# ---------------------------------------------------------------- structure

def find_cuts(frames: list[dict]) -> list[int]:
    return [i for i in range(1, len(frames)) if frames[i]["scene"] >= T["cut_scene"]]


def find_jumps(frames: list[dict], cuts: list[int]) -> list[int]:
    """One-frame discontinuities too small to be hard cuts.

    These are jump cuts in a talking head, hidden joins between generated clips, or an
    element snapping on in motion graphics. The sign is a scene-score spike well above
    its neighbours, together with a motion spike. The frame after a jump often carries
    residual change, so it is left out of the comparison.
    """
    cutset, out = set(cuts), []
    for i in range(3, len(frames) - 3):
        if any(abs(i - c) <= 1 for c in cutset):
            continue
        sc, yd = frames[i]["scene"], frames[i]["ydif"]
        nb = max(f["scene"] for f in frames[i - 3:i] + frames[i + 2:i + 4])
        ynb = max(f["ydif"] for f in frames[i - 3:i])
        if sc >= T["jump_scene"] and sc >= 3 * max(nb, 0.002) and yd >= 1.0 and yd >= 3 * max(ynb, 0.1):
            out.append(i)
    # Real edits don't cluster: jumps a few frames apart are stepped animation (drawn "on 4s")
    # or flicker, and a jump right next to a cut is the cut's aftermath.
    t = [f["t"] for f in frames]
    near = lambda i, others: any(o != i and abs(t[o] - t[i]) < 0.3 for o in others)  # noqa: E731
    return [i for i in out if not near(i, out) and not near(i, cuts)]


def find_gradual(frames: list[dict], cuts: list[int], fps: float) -> list[tuple[int, int]]:
    """Soft transitions: dissolves, fades, whips.

    ffmpeg's scene score ignores steady change by design, so a dissolve scores ~0.
    Two detectors cover it:
      A. moderate scene scores that add up to a scene change (whips, speed ramps);
      B. steady per-frame change with a one-way brightness ramp and quieter frames on
         both sides (dissolves and fades). A dissolve between two moving shots can
         slip past B; on the timeline sheet it shows as a ghosted double image.
    """
    cutset, out, n = set(cuts), [], len(frames)
    i = 1
    while i < n:
        if T["grad_low"] <= frames[i]["scene"] < T["cut_scene"] and i not in cutset:
            j = i
            while j + 1 < n and T["grad_low"] <= frames[j + 1]["scene"] < T["cut_scene"] and (j + 1) not in cutset:
                j += 1
            if j - i + 1 >= T["grad_min_frames"] and sum(f["scene"] for f in frames[i:j + 1]) >= T["cut_scene"] * 1.5:
                out.append((i, j))
            i = j + 1
        else:
            i += 1

    def avg(xs):
        return sum(xs) / len(xs) if xs else 0.0

    mot = [f["ydif"] for f in frames]
    pad, min_len = max(3, int(0.3 * fps)), max(T["grad_min_frames"], int(0.25 * fps))
    i = 1
    while i < n:
        if mot[i] >= 1.0 and i not in cutset:
            j = i
            while j + 1 < n and mot[j + 1] >= 1.0 and (j + 1) not in cutset:
                j += 1
            ys = [frames[k]["yavg"] for k in range(i - 1, j + 1)]
            total = ys[-1] - ys[0]
            steps = [b - a for a, b in zip(ys, ys[1:])]
            one_way = sum(1 for s in steps if s * total > 0) / max(len(steps), 1)
            inside = avg(mot[i:j + 1])
            quiet = avg(mot[max(1, i - pad):i]) < 0.6 * inside and avg(mot[j + 1:j + 1 + pad]) < 0.6 * inside
            if j - i + 1 >= min_len and abs(total) >= 8 and one_way >= 0.8 and quiet \
                    and not any(a <= j and i <= b for a, b in out):
                out.append((i, j))
            i = j + 1
        else:
            i += 1
    return sorted(out)


def runs(mask: list[bool]) -> list[tuple[int, int]]:
    out, start = [], None
    for i, m in enumerate(mask + [False]):
        if m and start is None:
            start = i
        elif not m and start is not None:
            out.append((start, i - 1))
            start = None
    return out


# ---------------------------------------------------------------- images

def extract_tiles(video: Path, work: Path, idx: list[int], font: str | None) -> dict[int, Path]:
    tiles = work / "frames" / "tiles"
    tiles.mkdir(parents=True, exist_ok=True)
    for old in tiles.glob("*.png"):
        old.unlink()
    label = ""
    if font:
        label = (f",drawtext=fontfile='{esc(font)}':text='%{{pts\\:hms}}  f%{{n}}':x=6:y=6:fontsize=15"
                 ":fontcolor=white:box=1:boxcolor=black@0.65:boxborderw=4")
    # ffmpeg's expression parser rejects very long sums, so split the wanted frames into
    # chunks, each selected on its own branch of one decode pass.
    chunks = [idx[k:k + 50] for k in range(0, len(idx), 50)]
    graph = (f"[0:v:0]setpts=PTS-STARTPTS,scale={TILE_W}:-2:flags=area{label},split={len(chunks)}"
             + "".join(f"[s{j}]" for j in range(len(chunks))))
    for j, ch in enumerate(chunks):
        graph += f";[s{j}]select='" + "+".join(f"eq(n\\,{i})" for i in ch) + f"'[o{j}]"
    cmd = ["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", video, "-filter_complex", graph]
    for j in range(len(chunks)):
        cmd += ["-map", f"[o{j}]", "-fps_mode", "passthrough", f"frames/tiles/c{j:03d}_%05d.png"]
    run(cmd, cwd=work)
    out = {}
    for j, ch in enumerate(chunks):
        for i, p in zip(ch, sorted(tiles.glob(f"c{j:03d}_*.png"))):
            dest = tiles / f"f{i:06d}.png"
            p.replace(dest)
            out[i] = dest
    return out


def make_sheets(name: str, idx: list[int], tiles: dict[int, Path], cols: int, rows: int,
                work: Path) -> list[str]:
    files = [tiles[i] for i in idx if i in tiles]
    per, made = cols * rows, []
    for k in range(0, len(files), per):
        chunk = files[k:k + per]
        n = k // per + 1
        rows_here = min(rows, math.ceil(len(chunk) / cols))  # no empty rows on the last sheet
        lst = work / "sheets" / f".{name}_{n:02d}.ffconcat"
        body = "ffconcat version 1.0\n"
        for f in chunk:
            body += "file '" + f.resolve().as_posix().replace("'", "'\\''") + "'\nduration 1\n"
        lst.write_text(body, encoding="utf-8")
        out = f"sheets/{name}_{n:02d}.png"
        run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
             "-vf", f"tile={cols}x{rows_here}:padding=4:margin=4:color=0x1a1a1a", "-frames:v", "1",
             "-fps_mode", "passthrough", out], cwd=work)
        lst.unlink(missing_ok=True)
        made.append(out)
    return made


def parse_spans(specs: list[str] | None, times: list[float]) -> list[tuple[float, float, list[int]]]:
    out = []
    for sp in specs or []:
        m = re.match(r"^\s*([\d.]+)\s*-\s*([\d.]+)\s*$", sp)
        if not m:
            sys.exit(f"hooks: bad --span '{sp}', use START-END in seconds")
        a, b = float(m[1]), float(m[2])
        out.append((a, b, [i for i, t in enumerate(times) if a <= t < b]))  # end is exclusive
    return out


def spans_only(video: Path, work: Path, args) -> list[str]:
    """Add every-frame sheets for --span windows to an existing review folder, without re-measuring."""
    fcsv = work / "frames.csv"
    if not fcsv.exists():
        sys.exit("hooks: --spans-only needs an earlier full run in the same --out folder")
    with open(fcsv, encoding="utf-8") as fh:
        times = [float(r["t"]) for r in csv.DictReader(fh)]
    span_sets = parse_spans(args.span, times)
    tiles = extract_tiles(video, work, sorted({i for _, _, ids in span_sets for i in ids}), find_font(args.font))
    made = []
    for a, b, ids in span_sets:
        made += make_sheets(f"span_{a:05.2f}-{b:05.2f}", ids, tiles, 5, 3, work)
    shutil.rmtree(work / "frames" / "tiles", ignore_errors=True)
    return made


def first_frame_views(video: Path, work: Path, last_idx: int) -> dict:
    fr = work / "frames"
    run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", video, "-map", "0:v:0", "-an", "-sn",
         "-vf", f"setpts=PTS-STARTPTS,select='eq(n\\,0)+eq(n\\,{last_idx})'", "-fps_mode", "passthrough",
         "frames/full_%d.png"], cwd=work)
    (fr / "full_1.png").replace(fr / "first_frame.png")
    if (fr / "full_2.png").exists():
        (fr / "full_2.png").replace(fr / "last_frame.png")
    else:
        shutil.copy(fr / "first_frame.png", fr / "last_frame.png")
    # Approximate areas covered by feed UI on Shorts/TikTok/Reels (title and channel at the
    # bottom, action buttons on the right, search/top bar). They vary by app and device.
    zones = ("drawbox=x=0:y=0:w=iw:h=ih*0.08:color=red@0.35:t=fill,"
             "drawbox=x=0:y=ih*0.74:w=iw:h=ih*0.26:color=red@0.35:t=fill,"
             "drawbox=x=iw*0.84:y=ih*0.40:w=iw*0.16:h=ih*0.34:color=red@0.35:t=fill,"
             "drawbox=x=iw/2-1:y=0:w=2:h=ih:color=white@0.5:t=fill,"
             "drawbox=x=0:y=ih/2-1:w=iw:h=2:color=white@0.5:t=fill")
    run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", "frames/first_frame.png", "-vf", zones,
         "frames/first_frame_safezones.png"], cwd=work)
    run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", "frames/first_frame.png",
         "-vf", "scale=180:-2:flags=area", "frames/first_frame_small.png"], cwd=work)
    run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", "frames/first_frame.png",
         "-vf", "scale=270:-2:flags=area,format=gray,gblur=sigma=6", "frames/first_frame_squint.png"], cwd=work)
    p = run(["ffmpeg", "-hide_banner", "-i", "frames/last_frame.png", "-i", "frames/first_frame.png",
             "-lavfi", "[0:v][1:v]ssim", "-f", "null", "-"], cwd=work, check=False)
    m = re.search(r"All:([\d.]+)", p.stderr)
    return {"loop_ssim": float(m[1]) if m else None}


# ---------------------------------------------------------------- analysis

def analyze(args) -> dict:
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"hooks: {tool} not found on PATH. Install ffmpeg 6+ (https://ffmpeg.org/download.html).")
    video = Path(args.video).resolve()
    if not video.is_file():
        sys.exit(f"hooks: no such file: {video}")
    work = Path(args.out or (video.parent / f"{video.stem}.hooks")).resolve()
    (work / "frames").mkdir(parents=True, exist_ok=True)
    (work / "sheets").mkdir(parents=True, exist_ok=True)
    if args.spans_only:
        return {"out": str(work), "spans_only": spans_only(video, work, args)}
    for old in (work / "sheets").glob("*.png"):
        old.unlink()
    if args.target_seconds:
        T["target_seconds"] = args.target_seconds

    info = probe(video)
    print(f"hooks: {video.name}  {info['width']}x{info['height']}  {info['fps']}fps  {info['duration']}s",
          file=sys.stderr)
    frames, blacks, freezes, thumbs = frame_pass(video, work)
    if not frames:
        sys.exit("hooks: no frames decoded")
    times = [f["t"] for f in frames]
    dur = info["duration"] or times[-1]
    fps = info["fps"] or (len(frames) / dur if dur else 30.0)
    n_frames = len(frames)
    change = visual_change(thumbs, fps)
    change += [0.0] * (n_frames - len(change))
    for f, c in zip(frames, change):
        f["change"] = c
    proxy_h = 2 * round(PROXY_W * info["height"] / info["width"] / 2)

    def idx_at(t: float) -> int:
        i = bisect.bisect_left(times, t)
        if i <= 0:
            return 0
        if i >= n_frames:
            return n_frames - 1
        return i if abs(times[i] - t) < abs(times[i - 1] - t) else i - 1

    def mean(xs):
        xs = list(xs)
        return sum(xs) / len(xs) if xs else 0.0

    flags: list[dict] = []

    def flag(sev, code, t0, t1, evidence, why, verify):
        flags.append({"severity": sev, "code": code, "t": round(t0, 3) if t0 is not None else None,
                      "t_end": round(t1, 3) if t1 is not None else None,
                      "evidence": evidence, "why": why, "verify": verify})

    # ---- format
    expected = dur * fps
    if expected and abs(n_frames - expected) > max(3, 0.03 * expected):
        flag("MAJOR", "DECODE_MISMATCH", None, None,
             f"decoded {n_frames} frames, expected ~{expected:.0f} ({dur:.2f}s at {fps} fps)",
             "Frames failed to decode or the stream is variable-rate. Times in this report may be shifted; "
             "re-export the file before trusting frame-level findings.", "frames.csv")
    aspect = info["width"] / info["height"]
    if abs(aspect - 9 / 16) > 0.02:
        flag("MAJOR", "NOT_VERTICAL_9x16", None, None, f"{info['width']}x{info['height']} (aspect {aspect:.3f})",
             "Short-form feeds are 9:16. Anything else is letterboxed or cropped by the app.", "frames/first_frame.png")
    if min(info["width"], info["height"]) < 1080:
        flag("MINOR", "BELOW_1080P", None, None, f"{info['width']}x{info['height']}",
             "Upload at 1080x1920 or higher; low resolution looks soft next to other videos.", "")
    lo, hi = T["target_seconds"] - T["target_band"], T["target_seconds"] + T["target_band"]
    if dur > 60:
        flag("MINOR", "LONG_FOR_A_SHORT", None, None, f"{dur:.1f}s",
             "Every second past ~35s must earn its place; completion rate is harder to hold.", "seconds.csv")
    elif not lo <= dur <= hi:
        flag("INFO", "LENGTH_OFF_TARGET", None, None, f"{dur:.1f}s vs {lo:.0f}-{hi:.0f}s",
             "Jenny Hoyos reported ~33-34s as her sweet spot. Treat it as a hypothesis to test, not a rule.", "")

    # ---- cuts and shots. Edit points = hard cuts + jumps + any the user gave with --edits.
    cuts = find_cuts(frames)
    jumps = find_jumps(frames, cuts)
    edits = {c: "cut" for c in cuts}
    for j in jumps:
        edits[j] = "jump"
    for t in args.edits or []:
        i = idx_at(t)
        near = [k for k in edits if abs(k - i) <= 2]
        if near:
            edits[near[0]] += "+given"
        else:
            edits[i] = "given"
    edit_points = sorted(edits.items())
    bounds = [0] + cuts + [n_frames]
    shots = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        t0 = times[a]
        t1 = times[b] if b < n_frames else dur
        seg = frames[a + 1:b]
        shots.append({"start_frame": a, "end_frame": b - 1, "start": round(t0, 3), "end": round(t1, 3),
                      "seconds": round(t1 - t0, 3), "frames": b - a,
                      "motion": round(mean(f["ydif"] for f in seg), 2) if seg else 0.0,
                      "yavg": round(mean(f["yavg"] for f in frames[a:b]), 1)})
    for k, s in enumerate(shots):
        if s["frames"] <= T["flash_frames"] and len(shots) > 1:
            where = "first" if k == 0 else ("last" if k == len(shots) - 1 else "mid")
            if k == 0:
                flag("BLOCKER", "FIRST_FRAME_STRAY", s["start"], s["end"],
                     f"shot 1 lasts {s['frames']} frame(s); frame 0 belongs to a different shot than what follows",
                     "The first frame is the poster that decides the swipe. A leftover frame wastes it.",
                     "sheets/hook_01.png, frames/first_frame.png")
            else:
                flag("MAJOR", "FLASH_FRAME", s["start"], s["end"],
                     f"{where} shot of {s['frames']} frame(s) at f{s['start_frame']}",
                     "1-2 frame shots are usually trim errors. Keep only if it is a deliberate flash.",
                     "sheets/cuts_*.png (look for this time)")
    gradual = find_gradual(frames, cuts, fps)
    for a, b in gradual:
        flag("MINOR", "GRADUAL_TRANSITION", times[a], times[b],
             f"{b - a + 1} frames of soft change (dissolve, fade, whip or fast camera move)",
             "Dissolves and fades slow a short down. A hard cut on action is usually stronger.",
             "sheets/transitions_*.png")

    # ---- visual changes and holds. Cuts plus big changes without a cut (animated
    # transitions, layout changes, reveals). A long hold is a stretch with neither.
    lag = max(1, round(0.5 * fps))
    cutset = set(cuts)
    soft = []
    for a, b in runs([c >= T["change_thr"] for c in change]):
        if any(a - lag <= c <= b for c in cutset):
            continue
        peak = max(range(a, b + 1), key=lambda k: change[k])
        soft.append(max(0, peak - lag // 2))
    marks = [0.0] + sorted(times[k] for k in cuts + soft) + [dur]
    holds = [(marks[k], marks[k + 1]) for k in range(len(marks) - 1)]
    n_changes = len(marks) - 2
    for t0, t1 in holds:
        if t1 - t0 >= T["hold_minor"]:
            sev = "MAJOR" if t1 - t0 >= T["hold_major"] else "MINOR"
            flag(sev, "LONG_HOLD", t0, t1, f"{t1 - t0:.1f}s with no cut and no big change on screen",
                 "Long holds invite a swipe unless something keeps changing: action, text, a reveal.",
                 "sheets/timeline_*.png over this range")

    # ---- black, frozen, static, letterbox
    for s, e in blacks:
        if s <= 0.05:
            flag("BLOCKER", "FIRST_FRAME_BLACK", s, e, f"black from {s:.2f}s to {e:.2f}s",
                 "A black first frame gives the viewer nothing to stop for.", "frames/first_frame.png")
        elif e >= dur - 0.1:
            flag("MAJOR", "FADE_TO_BLACK_END", s, e, f"black from {s:.2f}s to the end",
                 "Ending on black signals 'over' and breaks the replay loop.", "sheets/tail_01.png")
        else:
            flag("MAJOR", "BLACK_MID", s, e, f"black {e - s:.2f}s", "Black frames mid-video are dead time.",
                 "sheets/timeline_*.png")
    for s, e in freezes:
        if e - s >= T["freeze_minor"] and not any(bs <= s + 0.05 and be >= e - 0.05 for bs, be in blacks):
            sev = "MAJOR" if e - s >= T["freeze_major"] else "MINOR"
            flag(sev, "FROZEN_PICTURE", s, e, f"picture frozen {e - s:.2f}s",
                 "Frozen picture reads as a glitch or dead air. Intentional freeze-frames need text or sound doing work.",
                 "sheets/timeline_*.png")
    still = [f["ydif"] < T["static_ydif"] for f in frames]
    for a, b in runs(still):
        if any(c in cutset for c in range(a, b + 1)):
            continue
        t0, t1 = times[a], times[b]
        if t1 - t0 >= T["static_secs"] and not any(s <= t0 + 0.1 and e >= t1 - 0.1 for s, e in freezes):
            flag("MINOR", "STATIC_STRETCH", t0, t1, f"{t1 - t0:.1f}s of almost no motion",
                 "Nothing moving on screen. Check that text, voice or a reveal carries this stretch.",
                 "sheets/timeline_*.png")
    lb = []
    for f in frames:
        if f["crop_w"] is None or f["yavg"] < T["black_yavg"]:
            lb.append(False)
            continue
        lb.append(f["crop_h"] < T["letterbox_frac"] * proxy_h or f["crop_w"] < T["letterbox_frac"] * PROXY_W)
    for a, b in runs(lb):
        if times[b] - times[a] >= 0.5:
            fa = frames[(a + b) // 2]
            flag("MAJOR", "LETTERBOXED", times[a], times[b],
                 f"picture uses about {100 * fa['crop_w'] / PROXY_W:.0f}% width x {100 * fa['crop_h'] / proxy_h:.0f}% height",
                 "Bars waste the screen. Crop or reframe horizontal footage to fill 9:16.",
                 "sheets/timeline_*.png (dark scenes can false-alarm)")

    # ---- first frame and hook window
    f0 = frames[0]
    i05 = idx_at(0.5)
    if f0["yavg"] >= T["black_yavg"] and f0["yavg"] < 0.6 * frames[i05]["yavg"] and frames[i05]["yavg"] - f0["yavg"] > 30:
        flag("MAJOR", "FIRST_FRAME_FADE_IN", 0, times[i05],
             f"brightness {f0['yavg']:.0f} at frame 0 vs {frames[i05]['yavg']:.0f} at 0.5s",
             "Fading in hides the poster frame. Start on the full image.", "sheets/hook_01.png")
    hook_end = min(T["hook_window"], dur)
    hook_frames = [f for f in frames if f["t"] < hook_end]
    hook_cuts = [c for c in cuts if times[c] < hook_end]
    hook_motion = mean(f["ydif"] for f in hook_frames[1:])
    hook_soft = [k for k in soft if times[k] < hook_end]
    if not hook_cuts and not hook_soft and hook_motion < T["static_ydif"] * 2:
        flag("MAJOR", "HOOK_STATIC", 0, hook_end,
             f"no cut, no big change and low motion ({hook_motion:.2f}) in the first {hook_end:.0f}s",
             "The first seconds need visible change: the payoff preview, a punch-in, text popping on.",
             "sheets/hook_01.png")
    hook_yavg = mean(f["yavg"] for f in hook_frames)
    if hook_yavg < T["dark_hook_yavg"]:
        flag("MINOR", "DARK_OPENING", 0, hook_end, f"mean brightness {hook_yavg:.0f}/255 in the hook",
             "Dark openings read poorly on phones in daylight.", "sheets/hook_01.png")

    # ---- audio
    audio = audio_pass(video, work, dur) if info["has_audio"] else None
    if not info["has_audio"]:
        flag("MAJOR", "NO_AUDIO", None, None, "no audio stream",
             "Most viewers have sound on in the feed. Silence reads as broken.", "")
    elif audio:
        if audio["onset"] > T["audio_onset"]:
            flag("MAJOR", "LATE_AUDIO_START", 0, audio["onset"], f"silence until {audio['onset']:.2f}s",
                 "Sound should start on frame 1. A silent lead-in loses the swipe decision.", "")
        for s, e in audio["gaps"]:
            if e - s >= T["gap_secs"]:
                sev = "MAJOR" if e - s >= T["long_gap_secs"] else "MINOR"
                flag(sev, "DEAD_AIR", s, e, f"{e - s:.2f}s below -35 dB",
                     "Gaps between lines let attention drop. Tighten the cut or fill with sound.", "seconds.csv")
        if audio["tail_silence"] >= T["tail_secs"]:
            flag("MAJOR", "TAIL_DEAD_TIME", dur - audio["tail_silence"], dur,
                 f"last {audio['tail_silence']:.2f}s silent",
                 "Dead time at the end is where people swipe. Jenny Hoyos trimmed a final second and completion jumped.",
                 "sheets/tail_01.png")
        L = audio["integrated_lufs"]
        if L is not None and not T["lufs_low"] <= L <= T["lufs_high"]:
            flag("MINOR", "LOUDNESS", None, None, f"integrated {L} LUFS",
                 "Aim near -14 LUFS so the platform does not turn you down or leave you quiet.", "")
        tp = audio["true_peak_dbtp"]
        if tp is not None and tp > T["true_peak"]:
            flag("MINOR", "TRUE_PEAK", None, None, f"true peak {tp} dBTP", "Keep peaks at or below -1 dBTP to avoid clipping after encoding.", "")
        mom = audio["momentary"]
        last = [m for t, m in mom if t > dur - 0.8]
        before = [m for t, m in mom if dur - 2.3 < t <= dur - 0.8]
        if last and before and mean(before) - mean(last) > 8 and mean(last) > -60:
            flag("MINOR", "AUDIO_FADES_OUT", dur - 0.8, dur,
                 f"loudness falls {mean(before) - mean(last):.0f} LU in the last 0.8s",
                 "A fade-out says 'the end'. An abrupt stop makes people replay.", "sheets/tail_01.png")

    # ---- transcript
    tpath, tsource = (Path(args.transcript), "provided") if args.transcript else transcribe(video, work, info, args)
    transcript = load_transcript(tpath, dur, args.transcript_offset) if tpath else None
    lang_metrics, lang_flags, alignment = None, [], None
    if transcript:
        segs = transcript["segments"]
        script_text = Path(args.script).read_text(encoding="utf-8") if args.script else None
        if script_text and transcript["timed"]:
            script_text = trim_script(script_text, transcript["text"])
        if script_text:
            # A punctuated script gives true sentences; the transcript still gives timing.
            lang_metrics = rd.analyze_text(script_text)
            lang_metrics["text_source"] = f"script {args.script} (trimmed to what is spoken)"
        else:
            lang_metrics = rd.analyze_text(transcript["text"], lines=[s["text"] for s in segs])
            lang_metrics["text_source"] = "transcript"
        fs = lang_metrics["first_sentence"]
        if transcript["words"] and fs["size"]:
            n = min(fs["size"], len(transcript["words"]))
            fs["actual_seconds"] = round(transcript["words"][n - 1]["end"] - transcript["words"][0]["start"], 2)
        elif segs and fs["text"] == segs[0]["text"].strip():
            fs["actual_seconds"] = round(segs[0]["end"] - segs[0]["start"], 2)
        lang_flags = rd.flags_for(lang_metrics, dur if transcript["timed"] else None)
        text = transcript["text"]
        stops = len(re.findall(r"[.!?]", text))
        size = len(rd.en_words(text))
        if not script_text and size >= 30 and stops < size / 30:
            flag("INFO", "TRANSCRIPT_UNPUNCTUATED", None, None, f"{stops} sentence stops in {size} words",
                 "Sentences were guessed from pauses, so hook-line, last-line and reading-level numbers are rough. "
                 "Pass --script with the punctuated script for exact sentence checks.", "transcript")
        if transcript.get("clipped_from"):
            flag("INFO", "TRANSCRIPT_CLIPPED", None, None,
                 f"transcript runs to {transcript['clipped_from']}s; video is {dur:.1f}s",
                 "Only the part inside the video was used. If the short is not cut from the start, pass "
                 "--transcript-offset.", "transcript")
        if transcript["timed"] and audio:
            alignment = check_alignment(transcript, audio)
            if alignment["gaps"] >= 3 and alignment["matched"] < 0.6 * alignment["gaps"]:
                flag("MAJOR", "TRANSCRIPT_MISALIGNED", None, None,
                     f"only {alignment['matched']} of {alignment['gaps']} silences fall in pauses between words",
                     "Timing-based checks may be wrong. Check the offset (--transcript-offset) or the transcript.",
                     "transcript")
        for lf in lang_flags:
            if lf["code"] == "SCRIPT_TOO_LONG" or (lf["code"] == "REHOOK_GAP" and transcript["timed"]):
                continue  # length is checked against the video; rehook gaps are re-measured on real timings
            t0 = None
            if transcript["timed"]:
                if lf["code"] in ("HOOK_LINE_LONG",):
                    t0 = transcript["segments"][0]["start"]
                elif lf["code"] == "ENDING_LINE_LONG":
                    t0 = transcript["segments"][-1]["start"]
                elif lf["code"] == "FILLER_PHRASE":
                    hits = [s["start"] for s in transcript["segments"]
                            if any(p in s["text"].lower() for p in lang_metrics["fillers"]["hard"])]
                    t0 = hits[0] if hits else None
                    if t0 is not None and t0 < 5:
                        lf["why"] += " It sits inside the first 5 seconds."
            flag(lf["severity"], lf["code"], t0, None, lf["evidence"], lf["why"], "transcript")
        if transcript["timed"]:
            segs = transcript["segments"]
            first_t = (transcript["words"][0]["start"] if transcript["words"] else segs[0]["start"])
            last_t = (transcript["words"][-1]["end"] if transcript["words"] else segs[-1]["end"])
            if first_t > T["word_onset"]:
                flag("MAJOR", "LATE_FIRST_WORD", 0, first_t, f"first word at {first_t:.2f}s",
                     "The spoken hook should start on frame 1.", "transcript")
            if dur - last_t >= 1.0:
                flag("MAJOR", "TAIL_AFTER_LAST_WORD", last_t, dur, f"{dur - last_t:.2f}s after the last word",
                     "After the payoff line, every frame is a reason to leave. End within a beat.",
                     "sheets/tail_01.png")
            span = max(last_t - first_t, 1.0)
            rate = lang_metrics["words"] / span
            lang_metrics["spoken_rate"] = round(rate, 2)
            lang_metrics["spoken_rate_unit"] = "words/s"
            if rate < 2.0 or rate > 4.2:
                flag("MINOR", "SPEECH_RATE", first_t, last_t, f"{rate:.1f} words/s",
                     "Under 2 words/s drags; over ~4 strains non-native listeners.", "transcript")
            hook_text = _join([s["text"] for s in segs if s["start"] < hook_end])
            if transcript["words"]:
                hook_text = _join([w["word"] for w in transcript["words"] if w["start"] < hook_end])
            lang_metrics["spoken_in_hook_window"] = hook_text
            lang_metrics["first_word_at"] = round(first_t, 3)
            lang_metrics["last_word_end"] = round(last_t, 3)
            # Rehook candidates: spoken turns, timed by their own word when word timings exist,
            # otherwise by where they sit in their caption line.
            cands = []
            if transcript["words"]:
                ws = transcript["words"]
                offsets, text = [], ""
                for w in ws:
                    word = w["word"].strip()
                    text += "" if not text else " "
                    offsets.append(len(text))
                    text += word
                for k, marker in rd.find_turns(text):
                    j = max(0, bisect.bisect_right(offsets, k) - 1)
                    near = _join([w["word"] for w in ws[max(0, j - 4):j + 8]])
                    cands.append({"t": round(ws[j]["start"], 2), "marker": marker, "line": near})
            else:
                for s in segs:
                    for k, marker in rd.find_turns(s["text"]):
                        t = s["start"] + (s["end"] - s["start"]) * k / max(len(s["text"]), 1)
                        cands.append({"t": round(t, 2), "marker": marker, "line": s["text"].strip()})
            # The hook covers its first line, but never more than the hook window: an
            # unpunctuated transcript can make the "first line" the whole video.
            hook_line_end = min(segs[0]["end"], first_t + T["hook_window"])
            gap = rd.longest_gap(hook_line_end, last_t - rd.REHOOK_PAYOFF_SECS, [c["t"] for c in cands])
            limit = rd.rehook_limit(dur)
            lang_metrics["rehooks"] = {"candidates": cands, "timing": "transcript", "limit": limit,
                                       "longest_gap": [round(gap[0], 2), round(gap[1], 2)] if gap else None}
            if gap and gap[1] - gap[0] > limit:
                flag("MINOR", "REHOOK_GAP", gap[0], gap[1], f"{gap[1] - gap[0]:.1f}s with no spoken turn",
                     rd.REHOOK_GAP_WHY, "timeline sheets + transcript")

    # ---- images
    print("hooks: building contact sheets", file=sys.stderr)
    font = find_font(args.font)
    hook_fps = args.hook_fps
    hook_idx = sorted({idx_at(k / hook_fps) for k in range(int(hook_end * hook_fps))} | {0})
    step = 1.0 / args.sheet_fps
    if dur / step > 240:
        step = dur / 240
    tl_idx = sorted({idx_at(k * step) for k in range(int(dur / step) + 1)})
    tail_idx = sorted({idx_at(times[-1] - k / hook_fps) for k in range(1, 15)} | {n_frames - 1})
    cut_rows = [[max(0, c - 2), max(0, c - 1), c, min(n_frames - 1, c + 1)] for c, _ in edit_points]
    grad_rows = [[max(0, a - 1), a + (b - a) // 3, a + 2 * (b - a) // 3, min(n_frames - 1, b + 1)] for a, b in gradual]
    soft = [k for k in soft if not any(a - lag <= k <= b + lag for a, b in gradual)]
    grad_rows += [[max(0, k - lag), max(0, k - lag // 3), min(n_frames - 1, k + lag // 3), min(n_frames - 1, k + lag)]
                  for k in soft]
    seam_idx = [max(0, n_frames - 3), max(0, n_frames - 2), n_frames - 1, 0, min(1, n_frames - 1), min(2, n_frames - 1)]
    span_sets = parse_spans(args.span, times)
    want = set(hook_idx) | set(tl_idx) | set(tail_idx) | set(seam_idx)
    for r in cut_rows + grad_rows:
        want |= set(r)
    for _, _, ids in span_sets:
        want |= set(ids)
    tiles = extract_tiles(video, work, sorted(want), font)
    # Sheets stay within 1568 px on the long edge so image viewers show them unscaled.
    sheets = {
        "hook": make_sheets("hook", hook_idx, tiles, 5, 3, work),
        "cuts": make_sheets("cuts", [i for r in cut_rows for i in r], tiles, 4, 3, work),
        "transitions": make_sheets("transitions", [i for r in grad_rows for i in r], tiles, 4, 3, work),
        "timeline": make_sheets("timeline", tl_idx, tiles, 5, 3, work),
        "tail": make_sheets("tail", tail_idx, tiles, 5, 3, work),
        "loop_seam": make_sheets("loop_seam", seam_idx, tiles, 3, 2, work),
    }
    for a, b, ids in span_sets:
        sheets[f"span {a:.2f}-{b:.2f}"] = make_sheets(f"span_{a:05.2f}-{b:05.2f}", ids, tiles, 5, 3, work)
    shutil.rmtree(work / "frames" / "tiles", ignore_errors=True)
    views = first_frame_views(video, work, n_frames - 1)

    # ---- tables
    with open(work / "frames.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["frame", "t", "scene", "is_cut", "yavg", "sat", "ydif", "change", "crop_w_pct", "crop_h_pct"])
        for i, f in enumerate(frames):
            w.writerow([i, f"{f['t']:.3f}", f"{f['scene']:.3f}", int(i in cutset), f"{f['yavg']:.1f}",
                        f"{f['sat']:.1f}", f"{f['ydif']:.2f}", f"{f['change']:.1f}",
                        f"{100 * f['crop_w'] / PROXY_W:.0f}" if f["crop_w"] else "",
                        f"{100 * f['crop_h'] / proxy_h:.0f}" if f["crop_h"] else ""])
    seconds = []
    mom = audio["momentary"] if audio else []
    for s in range(int(math.ceil(dur))):
        fr = [f for f in frames if s <= f["t"] < s + 1]
        words = ""
        if transcript and transcript["timed"]:
            src = transcript["words"] or [{"start": x["start"], "word": x["text"]} for x in transcript["segments"]]
            words = _join([x["word"] for x in src if s <= x["start"] < s + 1])
        seconds.append({"s": s, "cuts": sum(1 for c in cuts if s <= times[c] < s + 1),
                        "motion": round(mean(f["ydif"] for f in fr), 2),
                        "change": round(max((f["change"] for f in fr), default=0.0), 1),
                        "brightness": round(mean(f["yavg"] for f in fr), 1),
                        "loudness": round(mean(m for t, m in mom if s < t <= s + 1), 1) if mom else None,
                        "words": words})
    with open(work / "seconds.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(seconds[0].keys()) if seconds else ["s"])
        w.writeheader()
        w.writerows(seconds)

    edit_rows = [{"n": k + 1, "kind": kind, "frame": c, "t": round(times[c], 3),
                  "score": round(frames[c]["scene"], 3),
                  "brightness_jump": round(frames[c]["yavg"] - frames[c - 1]["yavg"], 1) if c else 0.0,
                  "sheet": f"sheets/cuts_{k // 3 + 1:02d}.png", "row": k % 3 + 1}
                 for k, (c, kind) in enumerate(edit_points)]
    flags.sort(key=lambda f: (SEV_ORDER[f["severity"]], f["t"] if f["t"] is not None else -1))
    durations = [s["seconds"] for s in shots]
    report = {
        "video": str(video), "out": str(work), "info": info, "thresholds": T,
        "first_frame": {"brightness": round(f0["yavg"], 1), "saturation": round(f0["sat"], 1), **views},
        "hook": {"window": hook_end, "cuts": len(hook_cuts), "motion": round(hook_motion, 2),
                 "brightness": round(hook_yavg, 1)},
        "edits": edit_rows,
        "cuts": [e for e in edit_rows if e["kind"].startswith("cut")],
        "gradual": [{"start": round(times[a], 3), "end": round(times[b], 3), "frames": b - a + 1,
                     "sheet": f"sheets/transitions_{k // 3 + 1:02d}.png", "row": k % 3 + 1}
                    for k, (a, b) in enumerate(gradual)],
        "soft_changes": [{"t": round(times[k], 3), "frame": k, "strength": round(change[min(k + lag // 2, n_frames - 1)], 1),
                          "sheet": f"sheets/transitions_{(len(gradual) + j) // 3 + 1:02d}.png",
                          "row": (len(gradual) + j) % 3 + 1} for j, k in enumerate(soft)],
        "alignment": alignment,
        "shots": shots,
        "pace": {"shots": len(shots), "cuts_per_10s": round(10 * len(cuts) / dur, 2) if dur else 0,
                 "median_shot": round(statistics.median(durations), 2) if durations else 0,
                 "longest_shot": round(max(durations), 2) if durations else 0,
                 "visual_changes": n_changes,
                 "seconds_per_change": round(dur / (n_changes + 1), 2) if dur else 0,
                 "longest_hold": round(max((b - a for a, b in holds), default=0), 2)},
        "black": blacks, "freezes": freezes,
        "audio": {k: v for k, v in (audio or {}).items() if k != "momentary"} if audio else None,
        "transcript": {"source": tsource if tpath else None, "path": str(tpath) if tpath else None,
                       "timed": transcript["timed"], "text": transcript["text"],
                       "segments": transcript["segments"]} if transcript else None,
        "language": lang_metrics,
        "flags": flags, "sheets": sheets, "font": font, "frames_decoded": n_frames,
    }
    (work / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    (work / "report.md").write_text(render_md(report, seconds), encoding="utf-8")
    return report


# ---------------------------------------------------------------- report

def render_md(r: dict, seconds: list[dict]) -> str:
    i, L = r["info"], []
    add = L.append
    add(f"# Hooks measurements: {Path(r['video']).name}\n")
    add("Machine pass only. These are measured facts and candidate flags, not the review. "
        "Confirm every flag on the sheets before reporting it, and look for what the machine cannot see "
        "(story, hook promise, mechanism, on-screen text).\n")
    add("## File\n")
    add(f"- {i['width']}x{i['height']}, {i['fps']} fps, {i['duration']}s, {r['frames_decoded']} frames decoded, "
        f"{i['video_codec']}, {i['bitrate_kbps']} kbps")
    add(f"- audio: {i['audio_codec'] or 'none'}; subtitle streams: {i['subtitle_streams']}\n")

    add(f"## Auto-flags ({len(r['flags'])})\n")
    if r["flags"]:
        add("| sev | code | when | evidence | why it matters | look at |")
        add("|---|---|---|---|---|---|")
        for f in r["flags"]:
            when = "" if f["t"] is None else (fmt_t(f["t"]) + (f"-{fmt_t(f['t_end'])}" if f["t_end"] is not None else ""))
            add(f"| {f['severity']} | {f['code']} | {when} | {f['evidence']} | {f['why']} | {f['verify']} |")
    else:
        add("None. That only means nothing measurable broke; it says nothing about the hook or the story.")
    add("")

    ff = r["first_frame"]
    add("## First frame\n")
    add(f"- brightness {ff['brightness']}/255, saturation {ff['saturation']}")
    add(f"- loop seam similarity (last frame vs first frame, SSIM): {ff['loop_ssim']}")
    add("- views: `frames/first_frame.png` (full), `frames/first_frame_small.png` (feed/shelf size), "
        "`frames/first_frame_squint.png` (blurred grey: does one shape dominate?), "
        "`frames/first_frame_safezones.png` (red = usually covered by app UI)\n")

    h = r["hook"]
    add(f"## Hook window (0-{h['window']:.0f}s)\n")
    add(f"- cuts: {h['cuts']}, mean motion {h['motion']}, mean brightness {h['brightness']}")
    lm = r["language"]
    if lm and "spoken_in_hook_window" in lm:
        add(f"- spoken in the window: \"{lm['spoken_in_hook_window']}\"")
        add(f"- first word at {lm['first_word_at']}s")
    if r["audio"]:
        add(f"- audio starts at {r['audio']['onset']}s")
    add("")

    p = r["pace"]
    n_jumps = sum(1 for e in r["edits"] if e["kind"].startswith("jump"))
    add(f"## Edit points and transitions ({len(r['cuts'])} cuts, {n_jumps} jumps, {len(r['gradual'])} gradual, "
        f"{len(r['soft_changes'])} other big changes)\n")
    add(f"- {p['shots']} shots; {p['cuts_per_10s']} cuts per 10s; median shot {p['median_shot']}s; "
        f"longest {p['longest_shot']}s")
    add(f"- visual changes (cuts plus big changes without a cut): {p['visual_changes']}, about one every "
        f"{p['seconds_per_change']}s; longest hold {p['longest_hold']}s")
    if r["edits"]:
        add("- kinds: **cut** = hard cut; **jump** = a one-frame jolt too small for a cut (a jump cut in a talking "
            "head, a hidden join between generated clips, or an element snapping on); **given** = an edit point "
            "passed with --edits")
        add("- each row of a cuts sheet is one edit point: two frames before, then two after\n")
        add("| # | kind | time | frame | score | brightness jump | sheet, row |")
        add("|---|---|---|---|---|---|---|")
        for c in r["edits"]:
            add(f"| {c['n']} | {c['kind']} | {fmt_t(c['t'])} | f{c['frame']} | {c['score']} | "
                f"{c['brightness_jump']:+} | {c['sheet']} row {c['row']} |")
    else:
        add("- no edit points found. If you know where clips join, pass `--edits t1,t2,...` to get a sheet row "
            "for each.")
    for g in r["gradual"]:
        add(f"- gradual change {fmt_t(g['start'])}-{fmt_t(g['end'])} ({g['frames']} frames): {g['sheet']} row {g['row']}")
    for c in r["soft_changes"]:
        add(f"- big change without a cut (animated transition, layout change or reveal) around {fmt_t(c['t'])} "
            f"f{c['frame']} (strength {c['strength']}): {c['sheet']} row {c['row']}")
    add("")
    add("### Shots\n")
    add("| # | start | end | seconds | frames | motion | brightness |")
    add("|---|---|---|---|---|---|---|")
    for k, s in enumerate(r["shots"], 1):
        add(f"| {k} | {fmt_t(s['start'])} | {fmt_t(s['end'])} | {s['seconds']:.2f} | {s['frames']} | "
            f"{s['motion']} | {s['yavg']} |")
    add("")

    a = r["audio"]
    add("## Audio\n")
    if a:
        add(f"- integrated {a['integrated_lufs']} LUFS, range {a['lra_lu']} LU, true peak {a['true_peak_dbtp']} dBTP")
        add(f"- starts at {a['onset']}s; silent tail {a['tail_silence']}s")
        gaps = ", ".join(f"{s:.2f}-{e:.2f}s" for s, e in a["gaps"]) or "none"
        add(f"- gaps under -35 dB: {gaps}")
        add("- a music bed hides pauses in speech from this check; use the transcript timing too\n")
    else:
        add("- no audio\n")

    add("## Transcript and language\n")
    tr = r["transcript"]
    if not tr:
        add("- no transcript. Language, filler and hook-line checks were skipped. "
            "Pass `--transcript file.srt`, or `--whisper-model ggml.bin` / `--asr faster-whisper`.\n")
    else:
        add(f"- source: {tr['source']} ({tr['path']}), timed: {tr['timed']}")
        add(f"- sentence and readability numbers come from: {lm['text_source']}")
        if r.get("alignment"):
            al = r["alignment"]
            add(f"- alignment check: {al['matched']} of {al['gaps']} measured silences fall in pauses between words")
        add(f"- {lm['words']} words; Flesch-Kincaid grade {lm['fk_grade']}; reading ease {lm['flesch_reading_ease']}; "
            f"complex words {lm['pct_complex_words']}%")
        add(f"- hard words: {', '.join(lm['hard_words']) or '-'}")
        if "spoken_rate" in lm:
            add(f"- spoken rate: {lm['spoken_rate']} {lm['spoken_rate_unit']}")
        add(f"- number mentions: {lm['numbers']}")
        add(f"- filler: hard {lm['fillers']['hard'] or '-'}; soft {lm['fillers']['soft'] or '-'}")
        add(f"- first line: \"{lm['first_sentence']['text']}\"")
        add(f"- last line: \"{lm['last_sentence']['text']}\"\n")
        if tr["timed"]:
            add("| start | end | line |")
            add("|---|---|---|")
            for s in tr["segments"]:
                add(f"| {fmt_t(s['start'])} | {fmt_t(s['end'])} | {s['text']} |")
            add("")
        rh = lm.get("rehooks")
        if rh:
            timed = rh["timing"] == "transcript"
            at = (lambda c: fmt_t(c["t"])) if timed else (lambda c: f"~{c['est_seconds']}s")
            add("### Rehook candidates (spoken turns)\n")
            add("Turn words and questions where a new question may open. These are candidates: confirm each one "
                "in the transcript, and add the shown rehooks (a counter, a new obstacle, a reveal) from the "
                "timeline sheets. Build the rehook map from both (`references/hooks-and-rehooks.md`).\n")
            if rh["candidates"]:
                add("| time | marker | in |")
                add("|---|---|---|")
                for c in rh["candidates"]:
                    add(f"| {at(c)} | {c['marker']} | {c.get('line', c.get('context', ''))} |")
            else:
                add("- none found")
            if rh["longest_gap"]:
                a, b = rh["longest_gap"]
                when = f"{fmt_t(a)}-{fmt_t(b)}" if timed else f"~{a}-{b}s (estimated)"
                add(f"- longest stretch with no spoken turn, after the hook line and before the last "
                    f"{rd.REHOOK_PAYOFF_SECS:.0f}s: {when}, {b - a:.1f}s (limit {rh['limit']:.0f}s)")
            add("")

    add("## Per second\n")
    add(f"motion = frame-to-frame change; change = biggest difference vs 0.5s earlier "
        f"(over {T['change_thr']:.0f} counts as a visual change)\n")
    add("| s | cuts | motion | change | brightness | loudness | words |")
    add("|---|---|---|---|---|---|---|")
    for s in seconds:
        add(f"| {s['s']} | {s['cuts']} | {s['motion']} | {s['change']} | {s['brightness']} | {s['loudness']} | {s['words']} |")
    add("")

    add("## Look at these, in this order\n")
    order = [
        ("frames/first_frame.png", "cold read, as a muted stranger: what is this, and why stay? Decide before anything else"),
        ("frames/first_frame_small.png", "is it still readable at feed/shelf size?"),
        ("frames/first_frame_squint.png", "does one subject dominate, or is it mush?"),
        ("frames/first_frame_safezones.png", "is any text or the subject under the app UI?"),
    ]
    order += [(s, "first 3 seconds, 10 per second: what does a muted viewer understand by 3s?") for s in r["sheets"]["hook"]]
    order += [(s, "every edit point: does each one land on action or a word, and keep the eye where it was?")
              for s in r["sheets"]["cuts"]]
    order += [(s, "soft transitions and big changes without a cut: needed, and clean?")
              for s in r["sheets"]["transitions"]]
    order += [(s, "the whole video: beats, rehooks (said and shown; see the rehook candidates), dead stretches")
              for s in r["sheets"]["timeline"]]
    order += [(s, "the last ~1.5 seconds at 10 per second: abrupt end or a slow fade?") for s in r["sheets"]["tail"]]
    order += [(s, "the loop seam: top row = last three frames, bottom row = first three")
              for s in r["sheets"]["loop_seam"]]
    for k, v in r["sheets"].items():
        if k.startswith("span"):
            order += [(s, f"every frame, {k[5:]}s") for s in v]
    for n, (f, why) in enumerate(order, 1):
        add(f"{n}. `{f}`: {why}")
    if not r["font"]:
        add("\nNo font was found, so tiles have no time labels. Pass `--font path/to/font.ttf`.")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--out", help="output folder (default: <video>.hooks next to the video)")
    ap.add_argument("--transcript", help=".srt, .vtt, .json (whisper-style segments or words) or .txt")
    ap.add_argument("--whisper-model", help="whisper.cpp ggml model; uses ffmpeg's whisper filter (ffmpeg 8+)")
    ap.add_argument("--asr", choices=["none", "faster-whisper"], default="none",
                    help="transcribe with faster-whisper if no transcript is given (may download a model)")
    ap.add_argument("--asr-model", default="small")
    ap.add_argument("--script", help="punctuated script text; used for sentence and readability checks while "
                                     "timing still comes from --transcript (trimmed to what is spoken)")
    ap.add_argument("--transcript-offset", type=float, default=0.0,
                    help="seconds into the transcript where the video starts (for shorts cut from a longer video)")
    ap.add_argument("--edits", type=lambda s: [float(x) for x in s.split(",") if x.strip()],
                    help="known edit points in seconds, comma-separated (clip joins, EDL cuts)")
    ap.add_argument("--span", action="append", help="every frame in START-END seconds (end exclusive); repeatable")
    ap.add_argument("--spans-only", action="store_true",
                    help="only add --span sheets to an existing --out folder, without re-measuring")
    ap.add_argument("--hook-fps", type=float, default=10.0, help="frames per second sampled in the first 3s")
    ap.add_argument("--sheet-fps", type=float, default=2.0, help="frames per second on the timeline sheets")
    ap.add_argument("--target-seconds", type=float, help="target length (default 33.5)")
    ap.add_argument("--font", help="font file for tile labels")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    r = analyze(a)
    if "spans_only" in r:
        print("hooks: wrote " + ", ".join(r["spans_only"]))
        return
    counts = {}
    for f in r["flags"]:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    summary = ", ".join(f"{counts[k]} {k}" for k in SEV_ORDER if k in counts) or "no flags"
    print(f"hooks: {summary}. Read {Path(r['out']) / 'report.md'}")


if __name__ == "__main__":
    main()
