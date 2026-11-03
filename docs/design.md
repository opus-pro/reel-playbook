# Design: Topics and Hooks

How Topics fits with its companion skill, Hooks, and why.

## The goal

An agent goes from "what should I make next?" to a polished short-video script on its own, and the
loop closes when the posted video's results feed the next topic choice.

```
 channel profile + ledger ─────────────────────────────────────────┐
        │                                                          │
 1 SCOUT        topics: demand, saturation, room for an aha        │   Topics
 2 CONCEPT      2-3 angles per topic, as concept cards             │   Topics
 3 GATE         entertainment score, blind ── KILL ──> back to 1   │   Topics
        │  GREENLIGHT          └── REWORK (≤ 2) ──> back to 2      │
 4 SCRIPT       hooks first, story backwards, beat sheet, script   │   Hooks (Create)
 3b CHECK       did the aha, share line and pull survive?          │   Topics
 5 POLISH       paper review against the 9-dimension rubric        │   Hooks
 6 FINAL        script, first frame, shot plan, both scores        │   Topics
 7 LEARN        after posting: views ÷ subs, sends, follows ───────┘   Topics
```

## Two plugins, two skills

| Plugin | Skill | Job |
|---|---|---|
| `hooks` | `hooks` | The telling: hooks, rehooks, first frame, pacing, frame-by-frame review, hook-first scripts. Does not judge the idea. |
| `topics` | `topics` | The idea: topic research, concept cards, the entertainment score (concept, script and video modes), the full run and the Learn step. |

Why this split:

- **Hooks come first for most creators.** Many creators feel they already find good topics and need
  help with the telling. Hooks stays a focused, standalone skill for that stage.
- **Different creators care about different halves.** Separate plugins can be installed and improved
  on their own.
- **One skill each, with modes.** the Topics skill's research, scoring and pipeline share one vocabulary
  (the concept card, the three outcome scores), so splitting them into more skills would duplicate
  references and blur triggers. Hooks works the same way (Review, Create, Diagnose).
- **Script design stays in the Hooks skill's Create mode.** It already turns a premise into scored hooks,
  a beat sheet built backwards from the payoff, and a script checked for readability. Topics
  seeds it with the greenlit concept instead of copying it.
- **A topic is the first hook, but it is scored separately.** A hook is judged in the first 3 seconds
  and can be fixed in the edit; a topic is judged by what happens after the video (sends, the next
  video) and no edit saves it. The entertainment score is reported beside the Hooks skill's score, never
  added to it.

A marketplace that lists both plugins, so one command installs the pair, is a natural later step. No
code would be copied; each plugin keeps its own version and tests.

## The entertainment score

The full rubric is `skills/topics/references/entertainment-rubric.md`. In short:

- **Three outcomes:** an **aha** ("I'd never have thought of that"), wanting to **share** it ("I want
  others to know"), and wanting **more** (the channel, similar videos), as opposed to content that
  earns a like and stops.
- **Eight dimensions, 100 points:** Who cares 15, Fresh 10 (foundation); Surprise 15, Click 10 (Aha);
  Share motive 20, Arousal 10 (Share); Depth 10, Series and ownership 10 (More).
- **Floors over totals:** GREENLIGHT needs the bar (70, uncalibrated) plus Share motive ≥ 6 and
  Aha ≥ 6 or Arousal ≥ 7. KILL on Who cares ≤ 3, Fresh ≤ 2 or a false claim. REWORK otherwise, with
  three re-angles, at most twice.
- **Profiles:** like trap, dead-end news, trivia nobody asked for, smart but cold, rage bait, insider
  hit, hit shape. For example, a town with an animal for mayor, commentary on recent events and deep
  topics explained simply are hit shapes; a fact nobody cares about, a pleasant small-town piece that
  gets likes but no shares, and news nobody follows up are the failures.
- **Truth cap:** Click is capped at 4 when the core claim can't be checked.
- **Blind scoring:** in the full run the gate runs in a fresh subagent that sees only the concept
  cards.

## Design decisions

1. **What the score judges:** concepts (the gate) and scripts (value lost in writing), plus a video
   mode used from a Hooks review and for calibration.
2. **Markets:** English YouTube Shorts and Instagram Reels.
3. **Research sources:** open scripted sources only: yt-dlp for YouTube, Google Trends RSS,
   Wikipedia feeds, web search. No browser scraping, no API keys.

## Research sources tested (November 2026)

| Source | Works? | Notes |
|---|---|---|
| yt-dlp YouTube search, channel lists, per-video metadata | Yes | Per-video metadata needs a JavaScript runtime (`--js-runtimes node`). Views, likes, comments, subscribers, upload date. No share counts. |
| Google Trends daily RSS by country | Yes | |
| Wikipedia featured feed (most read, Did You Know, news) | Yes | DYK appears on some days only |
| Web search and fetch | Yes | Search results are US-centred |
| yt-dlp TikTok | No | Blocked |
| yt-dlp Bilibili search | No | HTTP 412 |
| Reddit JSON | No | Blocked without a browser user agent; spoofing one is out of bounds |
| Instagram | Not attempted | No open scripted source |

## Open items

- Calibrate the score (`docs/hooks-calibration.md`).
