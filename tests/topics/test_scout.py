#!/usr/bin/env python3
"""Offline checks for scout.py: the reach math, ranking, comment mining and feed parsing.

    python tests/topics/test_scout.py

No network: every source is a fixture in tests/topics/fixtures/.
"""
import contextlib
import datetime as dt
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / "tests" / "topics" / "fixtures"
sys.path.insert(0, str(ROOT / "skills" / "topics" / "scripts"))

import scout  # noqa: E402

TODAY = dt.date(2026, 11, 2)


def load(name):
    return json.loads((FIX / name).read_text(encoding="utf-8"))


class VideoMetrics(unittest.TestCase):
    def setUp(self):
        self.rows = {v["id"]: scout.video_metrics(v, TODAY) for v in load("videos.json")}

    def test_breakout(self):
        r = self.rows["breakout1"]
        self.assertAlmostEqual(r["views_per_sub"], 20.0)
        self.assertEqual(r["reach"], "BREAKOUT")
        self.assertEqual(r["age_days"], 10)
        self.assertAlmostEqual(r["views_per_day"], 200000.0)
        self.assertAlmostEqual(r["like_rate"], 0.06)

    def test_in_audience(self):
        self.assertEqual(self.rows["inaudience1"]["reach"], "in-audience")

    def test_tiny_channel_is_not_a_breakout(self):
        r = self.rows["tiny1"]
        self.assertGreater(r["views_per_sub"], 600)
        self.assertEqual(r["reach"], "too small")

    def test_mid_and_same_day_upload(self):
        r = self.rows["mid1"]
        self.assertEqual(r["reach"], "mid")
        self.assertEqual(r["age_days"], 1)

    def test_missing_fields(self):
        r = self.rows["nosubs1"]
        self.assertIsNone(r["views_per_sub"])
        self.assertIsNone(r["age_days"])
        self.assertEqual(r["reach"], "?")

    def test_ranking_puts_tiny_channels_last(self):
        order = [r["id"] for r in scout.rank_rows(list(self.rows.values()))]
        self.assertEqual(order[0], "breakout1")
        self.assertEqual(order[1], "mid1")
        self.assertLess(order.index("inaudience1"), order.index("tiny1"))


class Channel(unittest.TestCase):
    def test_outliers_against_median(self):
        entries = [{"id": str(i), "title": f"t{i}", "view_count": v}
                   for i, v in enumerate([100_000, 120_000, 90_000, 1_000_000, 20_000])]
        s = scout.channel_summary(entries, subs=200_000)
        self.assertEqual(s["median_views"], 100_000)
        tags = {r["id"]: r["tag"] for r in s["rows"]}
        self.assertEqual(tags["3"], "OUTLIER")
        self.assertEqual(tags["4"], "dud")
        self.assertEqual((s["outliers"], s["duds"]), (1, 1))
        self.assertAlmostEqual(s["rows"][3]["views_per_sub"], 5.0)

    def test_empty_channel(self):
        s = scout.channel_summary([], subs=None)
        self.assertIsNone(s["median_views"])
        self.assertEqual(s["count"], 0)


class Comments(unittest.TestCase):
    def test_mining(self):
        mined = scout.mine_comments(load("comments.json"))
        texts = [m["text"] for m in mined]
        kinds = {m["text"][:20]: m["kind"] for m in mined}
        self.assertEqual(mined[0]["likes"], 4100)                     # sorted by likes
        self.assertEqual(kinds["Part 2 with the cat "], "wants more")
        self.assertEqual(kinds["Now do one on the go"], "wants more")
        self.assertEqual(kinds["Wait, so who actuall"], "question")
        self.assertFalse(any("best thing" in t for t in texts))        # praise is not demand
        self.assertFalse(any(t.startswith("@someone") for t in texts))  # replies skipped
        self.assertNotIn("why?", texts)                                # too short to use


class Feeds(unittest.TestCase):
    def test_trends_rss(self):
        rows = scout.parse_trends_rss((FIX / "trends.xml").read_text(encoding="utf-8"), "US")
        self.assertEqual([r["query"] for r in rows], ["town elects dog", "daylight saving"])
        self.assertEqual(rows[0]["traffic"], "20000+")
        self.assertEqual(rows[0]["news"][0]["url"], "https://example.com/dog-term")
        self.assertEqual(len(rows[0]["news"]), 2)
        self.assertEqual(rows[1]["news"], [])

    def test_wiki_feed(self):
        f = scout.parse_wiki_feed(load("wiki_feed.json"))
        self.assertEqual(f["mostread"][0]["title"], "Halloween")
        self.assertEqual(f["dyk"][0],
                         "... that a dog has served as honorary mayor of a town for three terms?")
        self.assertEqual(f["dyk"][1], "... that octopuses taste with their arms?")
        self.assertEqual(f["news"], ["A comet becomes visible to the naked eye."])

    def test_wiki_feed_without_sections(self):
        f = scout.parse_wiki_feed({"tfa": {}})
        self.assertEqual((f["mostread"], f["dyk"], f["news"]), ([], [], []))


class Formatting(unittest.TestCase):
    def test_table_and_emit(self):
        rows = [{"reach": "BREAKOUT", "views_per_sub": 20.0, "views": 2_000_000,
                 "age_days": 1200, "title": "a | b"}]
        t = scout.md_table(rows, [("reach", "Reach"), ("views_per_sub", "Views÷subs"),
                                  ("views", "Views"), ("age_days", "Days"), ("title", "Title")])
        self.assertIn("| BREAKOUT | 20.00 | 2.0M | 1200 | a / b |", t)
        with tempfile.TemporaryDirectory() as d:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                scout.emit(t, rows, d, "search-x")
            self.assertTrue((Path(d) / "search-x.md").exists())
            self.assertEqual(json.loads((Path(d) / "search-x.json").read_text(encoding="utf-8")),
                             rows)

    def test_slug(self):
        self.assertEqual(scout.slug("Why Airplane Food?!"), "why-airplane-food")
        self.assertEqual(scout.slug("???"), "query")


if __name__ == "__main__":
    unittest.main(verbosity=2)
