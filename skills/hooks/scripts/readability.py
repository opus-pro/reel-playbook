#!/usr/bin/env python3
"""Readability and spoken-pacing checks for short-video scripts and transcripts.

Works on English text. Standard library only.

    python readability.py script.txt                # human-readable report
    python readability.py script.txt --json         # machine-readable
    python readability.py - < script.txt            # read stdin

The checks follow one idea: a stranger scrolling with their thumb should
understand every line the first time, at a 10-year-old's reading level.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

# Spoken rates used to estimate how long a script runs. Short-form narration
# is usually faster than conversation; tune with --rate.
DEFAULT_RATE = 2.8  # words/sec

# Lines that only clear the throat before the video starts. Any of these in a
# short is dead time; in the first 5 seconds they cost viewers.
FILLER_HARD = [
    "without further ado", "let's get started", "lets get started",
    "let's get into it", "let's dive in", "let's dive right in",
    "let's jump in", "let's jump right in", "hey guys", "hi guys",
    "what's up guys", "whats up guys", "welcome back", "welcome to my channel",
    "in this video", "in today's video", "today we're going to",
    "today i'm going to", "so today", "before we start", "before we begin",
    "make sure to subscribe", "don't forget to subscribe", "like and subscribe",
    "smash that like", "hit the bell", "let me know in the comments",
    "stay tuned", "let's find out", "let's look at", "let's take a look",
]
# Hedges and verbal tics. One is harmless; a cluster makes the line sag.
FILLER_SOFT = ["basically", "literally", "you know", "kind of", "sort of", "i mean",
               "um", "uh", "like, ", "so yeah", "pretty much", "in order to"]

# Words that turn a story: a "but", a twist, a new obstacle, a promise of what's next.
# Each one is a candidate rehook. Whether it really opens a new question is a judgment call.
TURN_MARKERS = ["but", "except", "until", "unless", "instead", "however", "turns out", "suddenly",
                "that's when", "here's the thing", "here's the catch", "here's why", "here's where",
                "the problem", "the catch", "the trick", "the twist", "plot twist", "the secret",
                "not even", "even worse", "even better", "or so i thought", "which means", "wait",
                "guess what", "guess which", "guess who", "guess how", "the last one", "the real",
                "most people"]
_TURN_RE = re.compile(r"\b(?:" + "|".join(re.escape(p) for p in sorted(TURN_MARKERS, key=len, reverse=True)) + r")\b")
REHOOK_PAYOFF_SECS = 3.0  # the last beat is the payoff; it needs no rehook
REHOOK_GAP_WHY = ("Nothing here opens a new question (no 'but', twist, obstacle or question). Look for a shown "
                  "rehook (a counter, a new obstacle); if there is none, add one where the beat resolves.")

# Everyday words a 10-year-old knows that the syllable count would call hard.
EN_COMMON_LONG = set(
    "every everyone everything everybody everywhere actually really already another anything anyone "
    "anybody anywhere family together remember beautiful different important probably usually "
    "video videos company money nobody somebody something sometimes someone everyday favorite "
    "favourite chocolate banana animal animals tomorrow yesterday hamburger computer camera "
    "interesting understand basically literally amazing instead whatever however especially "
    "eleven seventeen seventy hundred hundreds thousand million billion percent".split()
)
EN_NUMBER_WORDS = set(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen "
    "fourteen fifteen sixteen seventeen eighteen nineteen twenty thirty forty fifty "
    "sixty seventy eighty ninety hundred thousand million billion trillion percent "
    "half quarter dozen".split()
)

def en_syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", w)))


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p and p.strip(" \t,")]


def en_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9'’%.-]*", text)


def count_numbers(text: str) -> int:
    """Count number mentions. A run of number words ('twenty five hundred') counts once,
    so unpunctuated transcripts can merge neighbouring numbers and undercount."""
    runs, in_run = 0, False
    for tok in en_words(text):
        t = tok.lower().strip(".,")
        is_num = bool(re.search(r"\d", t)) or t in EN_NUMBER_WORDS or t.split("-")[0] in EN_NUMBER_WORDS
        if is_num and not in_run:
            runs += 1
        in_run = is_num
    return runs


def find_fillers(text: str) -> dict:
    low = text.lower()
    hard = [p for p in FILLER_HARD if p in low]
    hard = [p for p in hard if not any(p != q and p in q for q in hard)]  # keep only the longest match
    soft = {}
    for p in FILLER_SOFT:
        n = len(re.findall(r"\b" + re.escape(p.strip(", ")) + r"\b", low))
        if n:
            soft[p] = n
    return {"hard": hard, "soft": soft}


def spoken_seconds(text: str, rate: float) -> float:
    """Estimated time to say text aloud at rate words/s."""
    return len(en_words(text)) / rate


def find_turns(text: str) -> list[tuple[int, str]]:
    """Candidate rehooks: turn words ('but', 'until') and questions.

    Returns (character index, marker) pairs. Neighbouring hits count once, so
    'but wait' is one turn.
    """
    low = text.lower().replace("’", "'")
    hits = []
    for m in _TURN_RE.finditer(low):
        before = low[max(0, m.start() - 7):m.start()]
        if m.group() == "wait" and re.search(r"(?:can't|cannot) $", before):
            continue
        hits.append((m.start(), m.group()))
    # "Then the stove died." turns; "and then I added salt" doesn't
    hits += [(m.start(1), "then") for m in re.finditer(r"(?:^|[.!?]\s+)(then)\b", low)]
    hits += [(m.start(), "?") for m in re.finditer(r"\?", text)]
    out: list[tuple[int, str]] = []
    for i, marker in sorted(hits):
        if out and i - out[-1][0] < 12:
            continue
        out.append((i, marker))
    return out


def rehook_limit(seconds: float) -> float:
    """Longest stretch without a new question before it counts as a hole: about 10 s in
    a short, growing with length to the ~45 s ceiling long-form creators use."""
    return min(45.0, max(10.0, seconds / 6))


def longest_gap(start: float, end: float, times: list[float]) -> tuple[float, float] | None:
    """The longest stretch between start and end with no time in times."""
    if end <= start:
        return None
    pts = [start] + sorted(t for t in times if start < t < end) + [end]
    return max(zip(pts, pts[1:]), key=lambda p: p[1] - p[0])


def analyze_text(text: str, rate: float | None = None, lines: list[str] | None = None) -> dict:
    """Measure one block of script text.

    lines are the caption or transcript lines, if known. ASR and word-timing
    output often has no punctuation, so when the lines outnumber the
    punctuated sentences, the lines are used as sentences.
    """
    text = text.strip()
    rate = rate or DEFAULT_RATE
    sentences = split_sentences(text)
    if lines and len(lines) > len(sentences):
        sentences = [ln.strip() for ln in lines if ln.strip()]
    n_sent = max(len(sentences), 1)
    out: dict = {"sentences": len(sentences), "sentence_count_used": n_sent}

    words = en_words(text)
    n_words = max(len(words), 1)
    syl = [en_syllables(w) for w in words]
    n_syl = sum(syl)
    wps = n_words / n_sent
    spw = n_syl / n_words
    out.update({
        "units": "words",
        "words": len(words),
        "avg_words_per_sentence": round(wps, 1),
        "flesch_reading_ease": round(206.835 - 1.015 * wps - 84.6 * spw, 1),
        "fk_grade": round(0.39 * wps + 11.8 * spw - 15.59, 1),
        "pct_complex_words": round(100 * sum(1 for s in syl if s >= 3) / n_words, 1),
        "hard_words": sorted({w.lower().strip(".,!?") for w, s in zip(words, syl)
                              if (s >= 3 or len(w) >= 11) and not re.search(r"\d", w)
                              and w.lower().strip(".,!?") not in EN_COMMON_LONG})[:40],
        "longest_sentence_words": max((len(en_words(s)) for s in sentences), default=0),
        "est_seconds": round(spoken_seconds(text, rate), 1),
    })

    out["numbers"] = count_numbers(text)
    out["fillers"] = find_fillers(text)
    first = sentences[0] if sentences else ""
    last = sentences[-1] if sentences else ""
    size = lambda s: len(en_words(s))
    out["first_sentence"] = {"text": first, "size": size(first), "est_seconds": round(size(first) / rate, 1)}
    out["last_sentence"] = {"text": last, "size": size(last), "est_seconds": round(size(last) / rate, 1)}
    out["rate_used"] = rate
    # Rehooks: the hook line covers the opening, the payoff covers the end; every
    # stretch in between should have something that opens a new question.
    cands = [{"est_seconds": round(spoken_seconds(text[:i], rate), 1), "marker": marker,
              "context": " ".join(text[i:i + 48].split())} for i, marker in find_turns(text)]
    gap = longest_gap(out["first_sentence"]["est_seconds"], out["est_seconds"] - REHOOK_PAYOFF_SECS,
                      [c["est_seconds"] for c in cands])
    out["rehooks"] = {"candidates": cands, "longest_gap": [round(gap[0], 1), round(gap[1], 1)] if gap else None,
                      "limit": rehook_limit(out["est_seconds"]), "timing": "estimated"}
    return out


def flags_for(m: dict, target_seconds: float | None = None) -> list[dict]:
    """Turn measurements into review flags. Thresholds are Hooks defaults."""
    f = []
    unit = "words"

    def add(sev, code, evidence, why):
        f.append({"severity": sev, "code": code, "evidence": evidence, "why": why})

    g = m["fk_grade"]
    if g > 7:
        add("MAJOR", "READING_LEVEL_HIGH", f"Flesch-Kincaid grade {g}",
            "Aim for grade 5 or below (a 10-year-old). Swap long words for short ones.")
    elif g > 5:
        add("MINOR", "READING_LEVEL_HIGH", f"Flesch-Kincaid grade {g}",
            "Aim for grade 5 or below (a 10-year-old).")
    if m["fillers"]["hard"]:
        add("MAJOR", "FILLER_PHRASE", ", ".join(m["fillers"]["hard"]),
            "Throat-clearing lines are dead time. Cut straight to the content.")
    soft_total = sum(m["fillers"]["soft"].values())
    if soft_total >= 3:
        add("MINOR", "VERBAL_TICS", json.dumps(m["fillers"]["soft"], ensure_ascii=False),
            "A cluster of hedges makes lines sag. Cut most of them.")
    fs = m["first_sentence"]
    secs = fs.get("actual_seconds", fs["est_seconds"])
    if secs > 2.5:
        how = "spoken in" if "actual_seconds" in fs else "~"
        add("MAJOR", "HOOK_LINE_LONG", f"first sentence {fs['size']} {unit}, {how} {secs}s",
            "The hook line should land in about 2 seconds.")
    ls = m["last_sentence"]
    if ls["size"] > 8:
        add("MINOR", "ENDING_LINE_LONG", f"last sentence {ls['size']} {unit}",
            "A short, abrupt last line makes people replay. Long sign-offs let them swipe.")
    if target_seconds and m["est_seconds"] > target_seconds * 1.1:
        add("MAJOR", "SCRIPT_TOO_LONG", f"~{m['est_seconds']}s at {m['rate_used']} {unit}/s vs target {target_seconds}s",
            "Cut lines, not pace. Faster reading does not fix a long script.")
    secs = max(m["est_seconds"], 1)
    if m["numbers"] / secs * 10 > 2.5:
        add("MINOR", "NUMBER_DENSE", f"{m['numbers']} numbers in ~{m['est_seconds']}s",
            "More than about two numbers per 10 seconds overloads a scroller. Keep one number per beat, and small numbers.")
    rh = m.get("rehooks") or {}
    gap = rh.get("longest_gap")
    if gap and m["est_seconds"] >= 15 and gap[1] - gap[0] > rh["limit"]:
        add("MINOR", "REHOOK_GAP", f"~{gap[0]}-{gap[1]}s ({gap[1] - gap[0]:.0f}s) with no spoken turn",
            REHOOK_GAP_WHY)
    return f


def render(m: dict, flags: list[dict]) -> str:
    lines = [
        f"words: {m['words']}  sentences: {m['sentences']}  avg words/sentence: {m['avg_words_per_sentence']}",
        f"Flesch reading ease: {m['flesch_reading_ease']}  Flesch-Kincaid grade: {m['fk_grade']}  "
        f"complex words: {m['pct_complex_words']}%",
        f"hard words: {', '.join(m['hard_words']) or '-'}",
    ]
    lines += [
        f"estimated spoken length: {m['est_seconds']}s (rate {m['rate_used']}/s)",
        f"number mentions: {m['numbers']}",
        f"first sentence: \"{m['first_sentence']['text']}\" (~{m['first_sentence']['est_seconds']}s)",
        f"last sentence: \"{m['last_sentence']['text']}\"",
    ]
    rh = m["rehooks"]
    turns = ", ".join(f"~{c['est_seconds']}s {c['marker']}" for c in rh["candidates"]) or "none"
    lines.append(f"rehook candidates (spoken turns): {turns}")
    if rh["longest_gap"]:
        a, b = rh["longest_gap"]
        lines.append(f"longest stretch without one: ~{a}-{b}s ({b - a:.1f}s; limit {rh['limit']:.0f}s)")
    lines.append("flags:" if flags else "flags: none")
    for fl in flags:
        lines.append(f"  [{fl['severity']}] {fl['code']}: {fl['evidence']} -> {fl['why']}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="text file, or - for stdin")
    ap.add_argument("--rate", type=float, help="spoken rate in words/s")
    ap.add_argument("--target", type=float, help="target length in seconds")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.file == "-":
        if hasattr(sys.stdin, "reconfigure"):
            sys.stdin.reconfigure(encoding="utf-8")
        text = sys.stdin.read()
    else:
        with open(a.file, encoding="utf-8") as fh:
            text = fh.read()
    m = analyze_text(text, a.rate)
    fl = flags_for(m, a.target)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if a.json:
        print(json.dumps({"metrics": m, "flags": fl}, ensure_ascii=False, indent=2))
    else:
        print(render(m, fl))


if __name__ == "__main__":
    main()
