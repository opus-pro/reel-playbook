#!/usr/bin/env python3
"""Topic research from open sources: YouTube (via yt-dlp), Google Trends, Wikipedia.

Python standard library plus yt-dlp (`pip install yt-dlp`, run as `python -m yt_dlp`).

    python scout.py search "why airplane food is bland" --n 20     # outliers for a topic
    python scout.py search "dog sheriff" --recent --days 90         # newest first, last 90 days
    python scout.py channel https://www.youtube.com/@handle         # a channel's Shorts vs its median
    python scout.py comments https://www.youtube.com/shorts/ID      # questions and "part 2" asks
    python scout.py trends --geo US,GB                              # today's rising searches
    python scout.py wiki --lang en                                  # most-read and Did You Know

Every command prints a markdown report. --out DIR also saves it with the raw data as JSON.

The yardstick is views ÷ the channel's subscribers. Raw views mostly measure channel size. At about
1x or less a video stayed with the existing audience; at about 3x or more it reached strangers, which
is the best public sign that a topic travels.

Only open endpoints are used, with an honest user agent. Nothing here signs in, rotates identities
or works around a bot check; sources that need that are out of scope.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import statistics
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

USER_AGENT = "topics-scout/0.1"
SHORT_MAX_S = 180            # YouTube Shorts run up to 3 minutes
BREAKOUT = 3.0               # views ÷ subs at or above: reached strangers
IN_AUDIENCE = 1.0            # views ÷ subs at or below: stayed with subscribers
MIN_VIEWS = 10_000           # below this the ratio is noise (8 subs, 5K views is not a breakout)
CHANNEL_OUTLIER = 3.0        # x the channel's median views
CHANNEL_DUD = 0.3

# Comments that ask for more, or ask a question the video left open.
DEMAND_PATTERNS = [
    r"\bpart ?(2|two|ii)\b", r"\bnext (one|video|episode)\b", r"\bdo (one|a video) (on|about)\b",
    r"\bmore of (these|this)\b", r"\bnow do\b", r"\bplease make\b", r"\bwhat about\b",
]
QUESTION_START = re.compile(
    r"^(why|how|what|when|where|who|which|is|are|does|do|did|can|could|would|wait)\b", re.I)


# --------------------------------------------------------------------------- yt-dlp

def ytdlp_cmd() -> list[str]:
    exe = shutil.which("yt-dlp")
    return [exe] if exe else [sys.executable, "-m", "yt_dlp"]


_JS_FLAGS: list[str] | None = None


def js_flags() -> list[str]:
    """yt-dlp needs a JavaScript runtime for full YouTube metadata. Use node when it's there."""
    global _JS_FLAGS
    if _JS_FLAGS is None:
        _JS_FLAGS = []
        if shutil.which("deno") is None and shutil.which("node"):
            help_text = subprocess.run(ytdlp_cmd() + ["--help"], capture_output=True, text=True,
                                       encoding="utf-8", errors="replace").stdout
            if "--js-runtimes" in help_text:
                _JS_FLAGS = ["--js-runtimes", "node"]
    return _JS_FLAGS


def ytdlp_json(args: list[str], timeout: int = 180) -> dict | None:
    cmd = ytdlp_cmd() + ["-J", "--no-warnings", "--skip-download"] + args
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
    except FileNotFoundError:
        sys.exit("yt-dlp not found. Install it with: pip install yt-dlp")
    except subprocess.TimeoutExpired:
        print(f"  timed out: {' '.join(args[-1:])}", file=sys.stderr)
        return None
    if p.returncode != 0 or not p.stdout.strip():
        msg = (p.stderr.strip().splitlines() or ["no output"])[-1]
        print(f"  skipped {args[-1]}: {msg}", file=sys.stderr)
        return None
    return json.loads(p.stdout)


def video_info(url: str) -> dict | None:
    return ytdlp_json(js_flags() + [url])


# --------------------------------------------------------------------------- metrics

def parse_date(s: str | None) -> dt.date | None:
    if not s:
        return None
    try:
        return dt.datetime.strptime(s, "%Y%m%d").date()
    except ValueError:
        return None


def ratio(a, b) -> float | None:
    if a is None or not b:
        return None
    return a / b


def video_metrics(info: dict, today: dt.date) -> dict:
    """One row per video: reach relative to channel size, age, and reaction rates."""
    views = info.get("view_count")
    subs = info.get("channel_follower_count")
    likes = info.get("like_count")
    comments = info.get("comment_count")
    uploaded = parse_date(info.get("upload_date"))
    age = (today - uploaded).days if uploaded else None
    vs = ratio(views, subs)
    if vs is None:
        reach = "?"
    elif views < MIN_VIEWS:
        reach = "too small"
    elif vs >= BREAKOUT:
        reach = "BREAKOUT"
    elif vs <= IN_AUDIENCE:
        reach = "in-audience"
    else:
        reach = "mid"
    return {
        "id": info.get("id"),
        "title": (info.get("title") or "").strip(),
        "channel": info.get("channel") or info.get("uploader"),
        "url": info.get("webpage_url") or info.get("url"),
        "duration": info.get("duration"),
        "uploaded": uploaded.isoformat() if uploaded else None,
        "age_days": age,
        "views": views,
        "subs": subs,
        "views_per_sub": vs,
        "views_per_day": ratio(views, max(age, 1)) if age is not None else None,
        "like_rate": ratio(likes, views),
        "comment_rate": ratio(comments, views),
        "reach": reach,
    }


def rank_rows(rows: list[dict]) -> list[dict]:
    """Strongest public evidence first: views ÷ subs, then views per day. Videos under MIN_VIEWS go
    last, whatever their ratio."""
    return sorted(rows, key=lambda r: ((r["views"] or 0) >= MIN_VIEWS, r["views_per_sub"] or 0,
                                       r["views_per_day"] or 0), reverse=True)


def channel_summary(entries: list[dict], subs: int | None) -> dict:
    """Each Short against the channel's own median: what this audience already rewarded."""
    views = [e["view_count"] for e in entries if e.get("view_count") is not None]
    median = statistics.median(views) if views else None
    rows = []
    for e in entries:
        v = e.get("view_count")
        x = ratio(v, median)
        tag = ""
        if x is not None and x >= CHANNEL_OUTLIER:
            tag = "OUTLIER"
        elif x is not None and x <= CHANNEL_DUD:
            tag = "dud"
        rows.append({"id": e.get("id"), "title": (e.get("title") or "").strip(),
                     "url": e.get("url"), "views": v, "x_median": x,
                     "views_per_sub": ratio(v, subs), "tag": tag})
    return {"median_views": median, "subs": subs, "count": len(rows),
            "outliers": sum(r["tag"] == "OUTLIER" for r in rows),
            "duds": sum(r["tag"] == "dud" for r in rows), "rows": rows}


def classify_comment(text: str) -> str | None:
    t = text.strip()
    low = t.lower()
    if any(re.search(p, low) for p in DEMAND_PATTERNS):
        return "wants more"
    first = re.split(r"(?<=[.!?])\s*", t)[0]
    if "?" in t or QUESTION_START.match(first):
        return "question"
    return None


def mine_comments(comments: list[dict], limit: int = 40) -> list[dict]:
    out = []
    for c in comments:
        if c.get("parent", "root") != "root":     # replies are mostly people talking to each other
            continue
        text = (c.get("text") or "").replace("\n", " ").strip()
        kind = classify_comment(text) if len(text) >= 12 else None
        if kind:
            out.append({"kind": kind, "likes": c.get("like_count") or 0, "text": text[:240]})
    out.sort(key=lambda r: r["likes"], reverse=True)
    return out[:limit]


# --------------------------------------------------------------------------- web sources

def http_get(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


TRENDS_NS = {"ht": "https://trends.google.com/trending/rss"}


def parse_trends_rss(xml_text: str, geo: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    rows = []
    for item in root.iter("item"):
        news = []
        for n in item.findall("ht:news_item", TRENDS_NS):
            news.append({"title": (n.findtext("ht:news_item_title", "", TRENDS_NS) or "").strip(),
                         "url": n.findtext("ht:news_item_url", "", TRENDS_NS),
                         "source": n.findtext("ht:news_item_source", "", TRENDS_NS)})
        rows.append({"geo": geo, "query": (item.findtext("title") or "").strip(),
                     "traffic": item.findtext("ht:approx_traffic", "", TRENDS_NS),
                     "published": item.findtext("pubDate", ""), "news": news})
    return rows


def parse_wiki_feed(feed: dict) -> dict:
    most = feed.get("mostread") or {}
    read = [{"title": a.get("titles", {}).get("normalized") or a.get("title"),
             "views": a.get("views"), "extract": (a.get("extract") or "")[:200]}
            for a in most.get("articles", [])]
    dyk = [re.sub(r"\s+", " ", d.get("text") or re.sub(r"<[^>]+>", "", d.get("html", ""))).strip()
           for d in (feed.get("dyk") or [])]
    news = [re.sub(r"<[^>]+>", "", n.get("story", "")).strip() for n in (feed.get("news") or [])]
    return {"mostread_date": most.get("date"), "mostread": read, "dyk": dyk, "news": news}


# --------------------------------------------------------------------------- formatting

def fmt_num(v) -> str:
    if v is None:
        return "?"
    if isinstance(v, float):
        if v >= 100:
            return f"{v:,.0f}"
        return f"{v:.2f}" if v >= 0.1 else f"{v:.3f}"
    if v >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v / 1_000:.0f}K"
    return str(v)


def md_table(rows: list[dict], cols: list[tuple[str, str]]) -> str:
    head = "| " + " | ".join(h for _, h in cols) + " |"
    sep = "|" + "|".join("---" for _ in cols) + "|"
    body = []
    for r in rows:
        cells = []
        for key, _ in cols:
            v = r.get(key)
            if key.endswith("_days") or key == "likes":
                s = "" if v is None else str(v)
            elif isinstance(v, (int, float)) and not isinstance(v, bool):
                s = fmt_num(v)
            else:
                s = str(v or "")
            cells.append(s.replace("|", "/"))
        body.append("| " + " | ".join(cells) + " |")
    return "\n".join([head, sep] + body)


def slug(s: str) -> str:
    return re.sub(r"[^\w]+", "-", s.lower()).strip("-")[:50] or "query"


def emit(report: str, data, out: str | None, name: str) -> None:
    print(report)
    if out:
        d = Path(out)
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{name}.md").write_text(report + "\n", encoding="utf-8")
        (d / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2),
                                        encoding="utf-8")
        print(f"\nSaved {d / (name + '.md')} and .json", file=sys.stderr)


# --------------------------------------------------------------------------- commands

SEARCH_COLS = [("reach", "Reach"), ("views_per_sub", "Views÷subs"), ("views", "Views"),
               ("subs", "Subs"), ("age_days", "Days"), ("views_per_day", "Views/day"),
               ("like_rate", "Likes/view"), ("comment_rate", "Comments/view"),
               ("title", "Title"), ("channel", "Channel"), ("url", "URL")]


def cmd_search(a) -> None:
    prefix = "ytsearchdate" if a.recent else "ytsearch"
    flat = ytdlp_json(["--flat-playlist", f"{prefix}{a.n * 3}:{a.query}"])
    entries = (flat or {}).get("entries") or []
    picked = []
    for e in entries:
        d = e.get("duration")
        if a.shorts_only and d is not None and d > SHORT_MAX_S:
            continue
        picked.append(e)
        if len(picked) >= a.n:
            break
    today = dt.date.today()
    rows = []
    for i, e in enumerate(picked, 1):
        url = e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}"
        print(f"  [{i}/{len(picked)}] {url}", file=sys.stderr)
        info = video_info(url)
        if not info:
            continue
        r = video_metrics(info, today)
        if a.days and r["age_days"] is not None and r["age_days"] > a.days:
            continue
        rows.append(r)
    rows = rank_rows(rows)
    breakouts = [r for r in rows if r["reach"] == "BREAKOUT"]
    lines = [f"# Search: {a.query}", "",
             f"{len(rows)} videos ({'newest first' if a.recent else 'relevance'}"
             f"{', Shorts only' if a.shorts_only else ''}"
             f"{f', last {a.days} days' if a.days else ''}), taken {today.isoformat()}.",
             f"Breakouts (views ÷ subs ≥ {BREAKOUT:g}, at least {MIN_VIEWS:,} views): "
             f"{len(breakouts)}. In-audience (≤ {IN_AUDIENCE:g}): "
             f"{sum(r['reach'] == 'in-audience' for r in rows)}.",
             "", md_table(rows, SEARCH_COLS), "",
             "Reading it: breakouts are angles strangers chose. Many breakouts on one angle = proven "
             "but crowded; many in-audience results = tried and flat; few results = untouched."]
    emit("\n".join(lines), rows, a.out, f"search-{slug(a.query)}")


def cmd_channel(a) -> None:
    url = a.url.rstrip("/")
    if a.tab and not re.search(r"/(shorts|videos|streams)$", url):
        url += "/" + a.tab
    flat = ytdlp_json(["--flat-playlist", "--playlist-end", str(a.n), url])
    if not flat:
        sys.exit("Could not read the channel.")
    summary = channel_summary(flat.get("entries") or [], flat.get("channel_follower_count"))
    name = flat.get("channel") or flat.get("uploader") or url
    lines = [f"# Channel: {name}", "",
             f"Last {summary['count']} {a.tab or 'videos'}, taken {dt.date.today().isoformat()}. "
             f"Subscribers: {fmt_num(summary['subs'])}. Median views: {fmt_num(summary['median_views'])}. "
             f"Outliers (≥ {CHANNEL_OUTLIER:g}x median): {summary['outliers']}. "
             f"Duds (≤ {CHANNEL_DUD:g}x): {summary['duds']}.", "",
             md_table(summary["rows"], [("tag", "Tag"), ("x_median", "x median"),
                                        ("views_per_sub", "Views÷subs"), ("views", "Views"),
                                        ("title", "Title"), ("url", "URL")]),
             "", "Newest first. The newest few are still collecting views, so don't call them duds "
             "yet. View counts in channel lists are rounded. The titles are the ledger of what this "
             "channel has already made."]
    emit("\n".join(lines), {"channel": name, **summary}, a.out, f"channel-{slug(name)}")


def cmd_comments(a) -> None:
    info = ytdlp_json(js_flags() + ["--write-comments", "--extractor-args",
                                    f"youtube:max_comments={a.n};comment_sort=top", a.url],
                      timeout=300)
    if not info:
        sys.exit("Could not read the video.")
    comments = info.get("comments") or []
    mined = mine_comments(comments, a.limit)
    lines = [f"# Comments: {info.get('title', a.url)}", "",
             f"Read {len(comments)} top comments; {len(mined)} ask a question or ask for more.", "",
             md_table(mined, [("kind", "Kind"), ("likes", "Likes"), ("text", "Comment")]), "",
             "Questions the video left open are aha material for the next one. \"Wants more\" "
             "comments are direct demand."]
    emit("\n".join(lines), mined, a.out, f"comments-{info.get('id', 'video')}")


def cmd_trends(a) -> None:
    rows = []
    for geo in [g.strip().upper() for g in a.geo.split(",") if g.strip()]:
        try:
            rows += parse_trends_rss(http_get(f"https://trends.google.com/trending/rss?geo={geo}"), geo)
        except Exception as e:  # one country failing should not stop the rest
            print(f"  {geo}: {e}", file=sys.stderr)
    table = [{"geo": r["geo"], "query": r["query"], "traffic": r["traffic"],
              "news": r["news"][0]["title"] if r["news"] else ""} for r in rows]
    lines = [f"# Google Trends, daily ({a.geo})", "", f"Taken {dt.date.today().isoformat()}.", "",
             md_table(table, [("geo", "Geo"), ("query", "Search"), ("traffic", "Traffic"),
                              ("news", "Top headline")]), "",
             "Most of this is news and sport with a 1-3 day window. Use it for commentary topics "
             "and for spotting an evergreen topic that is suddenly being searched."]
    emit("\n".join(lines), rows, a.out, f"trends-{slug(a.geo)}")


def cmd_wiki(a) -> None:
    day = dt.date.fromisoformat(a.date) if a.date else dt.date.today() - dt.timedelta(days=1)
    url = (f"https://{a.lang}.wikipedia.org/api/rest_v1/feed/featured/"
           f"{day.year}/{day.month:02d}/{day.day:02d}")
    try:
        feed = parse_wiki_feed(json.loads(http_get(url)))
    except Exception as e:
        sys.exit(f"Could not read {url}: {e}")
    lines = [f"# Wikipedia ({a.lang}), feed for {day.isoformat()}", "",
             f"## Most read ({feed['mostread_date'] or 'n/a'})", "",
             md_table(feed["mostread"][:a.limit], [("views", "Views"), ("title", "Article"),
                                                   ("extract", "Extract")]), ""]
    if feed["dyk"]:
        lines += ["## Did you know", ""] + [f"- {t}" for t in feed["dyk"]] + [""]
    if feed["news"]:
        lines += ["## In the news", ""] + [f"- {t}" for t in feed["news"]] + [""]
    lines.append("Most-read spikes show what people are curious about right now. Did You Know items "
                 "are checked, surprising facts: raw aha material.")
    emit("\n".join(lines), feed, a.out, f"wiki-{a.lang}-{day.isoformat()}")


def main(argv: list[str] | None = None) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="find outliers for a topic on YouTube")
    s.add_argument("query")
    s.add_argument("--n", type=int, default=15, help="videos to measure (default 15)")
    s.add_argument("--recent", action="store_true", help="newest first instead of relevance")
    s.add_argument("--days", type=int, default=0, help="keep videos uploaded in the last N days")
    s.add_argument("--all-lengths", dest="shorts_only", action="store_false",
                   help="include videos longer than 3 minutes")
    s.set_defaults(func=cmd_search)

    c = sub.add_parser("channel", help="a channel's recent uploads against its own median")
    c.add_argument("url")
    c.add_argument("--n", type=int, default=50)
    c.add_argument("--tab", default="shorts", help="shorts (default), videos, or '' for the URL as given")
    c.set_defaults(func=cmd_channel)

    m = sub.add_parser("comments", help="questions and requests for more in a video's comments")
    m.add_argument("url")
    m.add_argument("--n", type=int, default=300, help="top comments to read")
    m.add_argument("--limit", type=int, default=40, help="rows to show")
    m.set_defaults(func=cmd_comments)

    t = sub.add_parser("trends", help="Google Trends daily searches by country")
    t.add_argument("--geo", default="US", help="comma-separated country codes, e.g. US,GB,CA,AU")
    t.set_defaults(func=cmd_trends)

    w = sub.add_parser("wiki", help="Wikipedia most-read, Did You Know and news")
    w.add_argument("--lang", default="en")
    w.add_argument("--date", help="YYYY-MM-DD (default yesterday)")
    w.add_argument("--limit", type=int, default=25)
    w.set_defaults(func=cmd_wiki)

    for sp in (s, c, m, t, w):
        sp.add_argument("--out", help="also save the report and raw JSON here")

    a = p.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
