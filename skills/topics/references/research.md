# Topic research

How to find what to make next: something the audience wants, that this channel hasn't already made,
with room for an aha. Read for Scout mode.

## Contents
1. The rules
2. Sources and commands
3. Reading the signals
4. The topic board
5. Platform notes: YouTube Shorts and Instagram Reels

---

## 1. The rules

- **Open sources and the user's own data only.** `scripts/scout.py` uses public endpoints with an
  honest user agent. Do not sign in on the user's behalf, rotate identities, spoof a browser, or work
  around a bot check or rate limit. If a source blocks you, note it and move on.
- **Every signal gets a date.** Views, trends and subscriber counts change daily. Write the date next
  to every number you carry into a concept card.
- **Evidence beats taste.** A topic goes on the board because a signal points at it (an outlier, a
  question in the comments, a rising search, a fresh fact), not because it sounds fun.
- **Don't copy outliers; learn from them.** An outlier shows that strangers wanted a topic or an
  angle. Find what made it travel and build a different concept on the same need. Remaking the same
  video puts the channel in the crowded column.

## 2. Sources and commands

All commands print a markdown report; `--out DIR` saves it with the raw JSON. Needs Python 3.9+ and
yt-dlp (`pip install yt-dlp`). Full YouTube metadata needs a JavaScript runtime; the script uses node
automatically when deno is absent.

| Need | Command | What you get |
|---|---|---|
| The channel's ledger and its own hits | `python <skill-dir>/scripts/scout.py channel URL --n 50` | Every recent Short with views, x the channel median, views ÷ subs; OUTLIER and dud tags |
| Demand and saturation for a topic | `scout.py search "query" --n 15` | Shorts on the topic ranked by views ÷ subs, with age, views per day, likes and comments per view |
| What's new on a topic | `scout.py search "query" --recent --days 60` | The same, newest first, limited to the window |
| Questions the audience is asking | `scout.py comments VIDEO_URL --n 300` | Top-level comments that ask a question or ask for more, by likes |
| What people are searching today | `scout.py trends --geo US,GB,CA,AU` | Google Trends daily searches with traffic and the top headline |
| What people are reading, and checked odd facts | `scout.py wiki --lang en` | Wikipedia most-read (yesterday), Did You Know and In the news |
| News, research, background | WebSearch, WebFetch | Articles and sources to verify claims; search results are US-centred |

More aha material, through WebSearch and WebFetch:

- Wikipedia's "Unusual articles" list and past Did You Know archives (checked, sourced oddities).
- University and journal press releases (new findings, often with a hidden why).
- Local news oddities: animals with jobs, odd local laws, records nobody expected.
- Court rulings, product recalls and policy changes (commentary with a consequence for viewers).

Each `search` measures every video individually, so 15 videos take a minute or two. Start narrow,
widen only for the topics that survive.

## 3. Reading the signals

### Reach: views ÷ subscribers

Raw views mostly measure channel size. Views ÷ the channel's subscribers is the fair comparison:

| Views ÷ subs | Reading |
|---|---|
| 3x or more (and at least 10,000 views) | **Breakout.** Strangers chose it; the strongest public sign a topic or angle travels. |
| About 1-3x | Reached somewhat past the audience. |
| 1x or less | **In-audience.** Stayed with subscribers; says little about strangers. |
| Under 10,000 views | Too small to read, whatever the ratio. |

Use views per day to compare videos of different ages: a 3-day-old Short at 2x may still be climbing.

### The channel's own outliers

`scout.py channel` compares each Short with the channel's median. An OUTLIER (3x the median or more)
is a topic this audience already rewarded: find its need and serve it again with a new angle. Duds
(0.3x or less) are topics to avoid repeating, unless the execution was clearly the problem. The
newest few Shorts are still collecting views; don't judge them yet.

### Saturation: is the angle crowded?

Search the concept's core point (not just the topic) and read the result:

| What the search shows | Reading | Effect on Fresh |
|---|---|---|
| Several recent breakouts making the same point | Proven but crowded | Change the angle; the same point scores 2-4 |
| Many recent videos, mostly in-audience | Tried, and strangers didn't care | Weak evidence against the topic; think twice |
| Old breakouts, nothing recent | Proven and resting: may be ready for a new take | 6-8 with a fresh angle |
| Almost nothing | Untouched: fresh but unproven | 7-9, and check Who cares harder |

### Reaction rates

- **Comments per view** high relative to similar videos: people had something to say. Often a debate
  or a question, which suggests Settle this or Depth.
- **Likes per view** high with modest reach: liked by the audience, not passed on. A hint of the like
  trap.
- **YouTube shows no share counts.** Don't infer shares from likes.

### Comments

`scout.py comments` keeps questions and requests for more. Questions the video left open are aha
material for a follow-up ("wait, who signs the dog's paperwork?"). Requests ("part 2", "now do one
on…") are direct demand, and the topic they name is a board candidate.

### Trends and the news window

Trends and news topics have a window: in short-form, roughly 1-3 days for breaking news and about a
week for a story that keeps developing. Past the window, Fresh drops to 2-4 unless the angle is new.
A sudden search spike on an evergreen topic (a season, a holiday, an anniversary) is often the better
find: the topic is proven and the interest is now.

## 4. The topic board

Collect 15-30 candidates from the signals, then filter fast. For each, one line: the topic, the
signal that put it there (with date), and a quick read on three things:

| Quick filter | Keep if | Drop if |
|---|---|---|
| **Who cares** | You can name three different strangers who'd stop | Only insiders care |
| **Fresh** | The angle isn't crowded and the channel hasn't made it | The ledger or the search says it's done |
| **Room for an aha** | You can already see a Before → After | It's a topic everyone already understands |

Keep 5-8, ranked. Then write 2-3 concept cards for each of the best 3-4, using the angles in
`angles.md`. The board itself goes in `assets/topic-board.md`.

**Not repetitive** means three checks: against the channel's ledger (titles and topics made), against
the board's own other cards (no two cards making the same point), and against the niche (the
saturation search).

## 5. Platform notes: YouTube Shorts and Instagram Reels

- **YouTube Shorts** is fully researchable with `scout.py`: search, channels, comments and
  subscriber counts are public.
- **Instagram Reels has no open scripted source.** Instagram blocks scripted access, and this skill
  doesn't work around it. Research Reels topics through YouTube Shorts (the same short-form formats
  and audiences mostly overlap), Google Trends, Wikipedia and the web. Use the user's own Instagram
  Insights (sends, follows, reach) in the Learn step; ask the user to paste them.
- **Cross-posting.** A topic that broke out on Shorts is a reasonable Reels candidate, but Instagram
  leans harder on sends, so the Share motive matters even more there.
- **What travels may differ.** Because Instagram weighs sends for reaching new people, concepts built
  on motives people act on in DMs ("This is so you", "LOL") may do relatively better on Reels. That
  is a hypothesis to check against the user's numbers, not a rule.
