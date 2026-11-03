#!/usr/bin/env python3
"""Build a 36-second vertical test video with known defects planted at known times.

    python tests/hooks/make_fixture.py OUT_DIR

Writes OUT_DIR/fixture.mp4 and OUT_DIR/fixture.srt. Timeline:

  0.00-0.50   black                        -> FIRST_FRAME_BLACK
  0.50-5.00   shot A (moving test pattern)
  5.00-5.07   2 red frames                 -> FLASH_FRAME
  5.07-12.00  shot B (mandelbrot zoom)
  12.00-14.00 still picture                -> FROZEN_PICTURE
  14.00-15.00 dissolve into shot C         -> GRADUAL_TRANSITION
  15.00-26.00 shot C, letterboxed 16:9     -> LETTERBOXED
  26.00-36.00 shot D, fades to black       -> FADE_TO_BLACK_END
  audio: silent until 1.2s, gap 20-21s, silent after 34.5s
         -> LATE_AUDIO_START, DEAD_AIR, TAIL_DEAD_TIME
  captions: greeting, long hook line, long sign-off -> FILLER_PHRASE, HOOK_LINE_LONG, ...
"""
import subprocess
import sys
from pathlib import Path

W, H, FPS = 1080, 1920, 30
ENC = ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-r", str(FPS)]

SRT = """1
00:00:01,300 --> 00:00:04,800
Hey guys, welcome back to my channel, today we're going to talk about something incredibly interesting regarding household economics.

2
00:00:05,000 --> 00:00:19,500
Basically the fundamental consideration is whether discretionary expenditure, you know, kind of correlates with consumer satisfaction.

3
00:00:21,000 --> 00:00:34,000
And that is the conclusion of our comprehensive investigation, so make sure to subscribe for more fascinating content.
"""


def ff(args, cwd):
    subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *args], cwd=cwd, check=True)


def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    seg = out / "segs"
    seg.mkdir(exist_ok=True)
    size = f"{W}x{H}"
    ff(["-f", "lavfi", "-i", f"color=black:s={size}:r={FPS}:d=0.5", *ENC, "s1.mp4"], seg)
    ff(["-f", "lavfi", "-i", f"testsrc2=s={size}:r={FPS}:d=4.5", *ENC, "s2.mp4"], seg)
    ff(["-f", "lavfi", "-i", f"color=red:s={size}:r={FPS}", "-frames:v", "2", *ENC, "s3.mp4"], seg)
    ff(["-f", "lavfi", "-i", f"mandelbrot=s=270x480:r={FPS}", "-frames:v", "208",
        "-vf", f"scale={W}:{H}", *ENC, "s4.mp4"], seg)
    still = f"smptehdbars=s={size}:r={FPS}:d=3"
    shot_c = f"testsrc2=s=1080x608:r={FPS}:d=12,pad={W}:{H}:0:(oh-ih)/2:black"
    ff(["-f", "lavfi", "-i", still, "-f", "lavfi", "-i", shot_c,
        "-filter_complex", "[0:v][1:v]xfade=transition=fade:duration=1:offset=2,format=yuv420p",
        *ENC, "s5.mp4"], seg)
    ff(["-f", "lavfi", "-i", f"life=s=270x480:mold=10:r={FPS}:ratio=0.1:death_color=#C83232:life_color=#00ff00",
        "-t", "10", "-vf", f"scale={W}:{H}:flags=neighbor,fade=t=out:st=9:d=1", *ENC, "s6.mp4"], seg)
    (seg / "list.txt").write_text("".join(f"file 's{i}.mp4'\n" for i in range(1, 7)))
    # Re-encode: stream-copying separately encoded x264 segments leaves undecodable frames.
    ff(["-f", "concat", "-safe", "0", "-i", "list.txt", *ENC, "video.mp4"], seg)
    tone = "0.3*sin(2*PI*440*t)"
    expr = f"{tone}*between(t\\,1.2\\,20)+{tone}*between(t\\,21\\,34.5)"
    ff(["-i", seg / "video.mp4", "-f", "lavfi", "-i", f"aevalsrc={expr}:s=48000:d=36",
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-shortest", "fixture.mp4"], out)
    (out / "fixture.srt").write_text(SRT, encoding="utf-8")
    print(out / "fixture.mp4")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "tests/out"))
