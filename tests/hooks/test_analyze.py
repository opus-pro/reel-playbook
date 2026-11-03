#!/usr/bin/env python3
"""Check that the analyzer finds every defect planted in the fixture video.

    python tests/hooks/test_analyze.py

Needs ffmpeg/ffprobe on PATH. Builds the fixture on first run (tests/out/).
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tests" / "out"
ANALYZE = ROOT / "skills" / "hooks" / "scripts" / "analyze.py"
READABILITY = ROOT / "skills" / "hooks" / "scripts" / "readability.py"

# code -> (expected start, tolerance in seconds); None = time not checked
EXPECTED = {
    "FIRST_FRAME_BLACK": (0.0, 0.1),
    "FLASH_FRAME": (5.0, 0.1),
    "FROZEN_PICTURE": (12.0, 0.3),
    "GRADUAL_TRANSITION": (14.0, 0.4),
    "LETTERBOXED": (14.5, 0.8),
    "FADE_TO_BLACK_END": (35.5, 0.6),
    "LATE_AUDIO_START": (0.0, 0.1),
    "DEAD_AIR": (20.0, 0.2),
    "TAIL_DEAD_TIME": (34.5, 0.2),
    "LATE_FIRST_WORD": (0.0, 0.1),
    "TAIL_AFTER_LAST_WORD": (34.0, 0.1),
    "FILLER_PHRASE": (1.3, 0.1),
    "HOOK_LINE_LONG": (1.3, 0.1),
    "ENDING_LINE_LONG": (21.0, 0.1),
    "READING_LEVEL_HIGH": None,
    "VERBAL_TICS": None,
    "REHOOK_GAP": (4.3, 0.1),  # nothing turns after the hook window (first word at 1.3 s + 3 s)
}


class AnalyzerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (OUT / "fixture.mp4").exists():
            subprocess.run([sys.executable, str(ROOT / "tests" / "hooks" / "make_fixture.py"), str(OUT)], check=True)
        subprocess.run([sys.executable, str(ANALYZE), str(OUT / "fixture.mp4"), "--out", str(OUT / "review"),
                        "--transcript", str(OUT / "fixture.srt"), "--span", "4.9-5.2", "--edits", "20.0"], check=True)
        cls.report = json.loads((OUT / "review" / "report.json").read_text(encoding="utf-8"))

    def test_given_edit_point_logged(self):
        given = [e for e in self.report["edits"] if "given" in e["kind"]]
        self.assertTrue(any(abs(e["t"] - 20.0) < 0.05 for e in given), f"edits: {self.report['edits']}")

    def test_spans_only_adds_sheet(self):
        subprocess.run([sys.executable, str(ANALYZE), str(OUT / "fixture.mp4"), "--out", str(OUT / "review"),
                        "--span", "11.9-12.1", "--spans-only"], check=True)
        self.assertTrue((OUT / "review" / "sheets" / "span_11.90-12.10_01.png").is_file())
        self.assertTrue((OUT / "review" / "sheets" / "hook_01.png").is_file(), "spans-only must keep other sheets")

    def test_planted_defects_found(self):
        flags = self.report["flags"]
        for code, when in EXPECTED.items():
            hits = [f for f in flags if f["code"] == code]
            self.assertTrue(hits, f"{code} not flagged")
            if when:
                t, tol = when
                self.assertTrue(any(f["t"] is not None and abs(f["t"] - t) <= tol for f in hits),
                                f"{code} at {[f['t'] for f in hits]}, expected ~{t}")

    def test_no_false_cut_inside_moving_shot(self):
        # Shot A (0.5-5.0s) is one continuous moving pattern: no cut may land inside it.
        inside = [c for c in self.report["cuts"] if 0.7 < c["t"] < 4.9]
        self.assertEqual(inside, [], f"spurious cuts {inside}")

    def test_outputs_exist(self):
        review = OUT / "review"
        for name in ["report.md", "frames.csv", "seconds.csv", "frames/first_frame.png",
                     "frames/first_frame_safezones.png", "frames/first_frame_small.png",
                     "frames/first_frame_squint.png", "frames/last_frame.png",
                     "sheets/hook_01.png", "sheets/cuts_01.png", "sheets/timeline_01.png",
                     "sheets/tail_01.png", "sheets/loop_seam_01.png", "sheets/span_04.90-05.20_01.png"]:
            self.assertTrue((review / name).is_file(), f"missing {name}")
        rows = (review / "frames.csv").read_text().strip().splitlines()
        self.assertEqual(len(rows) - 1, self.report["frames_decoded"], "frames.csv must have one row per frame")

    def test_readability_cli(self):
        p = subprocess.run([sys.executable, str(READABILITY), "-", "--json", "--target", "10"],
                           input="I spent one dollar on a burger. My dad tried it. He said wow.",
                           capture_output=True, text=True, encoding="utf-8", check=True)
        m = json.loads(p.stdout)["metrics"]
        self.assertLess(m["fk_grade"], 3)
        self.assertEqual(m["numbers"], 1)

    def test_rehooks_timed_from_transcript(self):
        rh = self.report["language"]["rehooks"]
        self.assertEqual(rh["timing"], "transcript")
        self.assertEqual(rh["candidates"], [])
        self.assertEqual(rh["limit"], 10.0)

    def test_readability_rehooks(self):
        script = ("My dad says a $60 umbrella is a scam. So we test both. But rain is easy. "
                  "Then Dad got the leaf blower, and then he smiled. I can't wait. Guess which one breaks.")
        p = subprocess.run([sys.executable, str(READABILITY), "-", "--json"], input=script,
                           capture_output=True, text=True, encoding="utf-8", check=True)
        markers = [c["marker"] for c in json.loads(p.stdout)["metrics"]["rehooks"]["candidates"]]
        self.assertEqual(markers, ["but", "then", "guess which"])
        flat = " ".join(["We wash the rice. We cook the rice. We eat the rice with soup."] * 9)
        p = subprocess.run([sys.executable, str(READABILITY), "-", "--json"], input=flat,
                           capture_output=True, text=True, encoding="utf-8", check=True)
        self.assertIn("REHOOK_GAP", [f["code"] for f in json.loads(p.stdout)["flags"]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
