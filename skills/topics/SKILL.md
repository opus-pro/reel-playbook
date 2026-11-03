---
name: topics
description: Find what to make next and judge whether a short-video idea is worth making, before anyone writes a hook. Researches topics from open sources (YouTube Shorts outliers by views ÷ subscribers, comments, Google Trends, Wikipedia), turns them into concept cards with a clear angle, and scores each concept, script or video topic for entertainment value - the aha ("I'd never have thought of that"), the urge to send it to someone, and the pull to watch more - so an idea that would only earn likes gets reworked or killed. Can run the whole pipeline from topic to a polished script, handing scripting and polish to Hooks. Use whenever someone asks what to post next, wants video ideas or topics for Shorts, Reels or TikTok, asks whether an idea is good, shareable, viral-worthy or worth making, wants concepts rated or compared, asks why a well-made video got likes but no shares, or wants a channel's next short planned end to end - even if they never say "topic".
---

# Topics

A short travels when strangers get an aha, send it to someone, and want more. Most of that is decided
by the topic and the angle, before a frame is shot: a well-told video about something nobody wants to
pass on still stops at a like. Topics finds topics worth making, shapes them into concepts, and
scores them for entertainment value. Hooks, its companion skill, then makes the telling as strong
as the idea.

## Pick the mode

| The user brings | Mode | You deliver |
|---|---|---|
| A channel, a niche, or "what should I post next?" | **Scout** | A topic board and concept cards, each with dated evidence |
| An idea, a concept, a script or a video, and "is this worth making?" | **Score** | An entertainment score: verdict, total, Aha / Share / More, profile, and re-angles or fixes |
| "Make my next short", or a channel and a goal | **Run** | The full pipeline: topic, concept, blind gate, script and polish (with Hooks), final package |
| A posted short's results | **Learn** | A ledger row, and what it changes for the next round |

## The stance

- **The idea, not the telling.** Before writing any note, ask: could an edit fix this? If yes, it is
  the Hooks skill's job. Never mark a concept down for a hook line, a first frame or pacing.
- **Evidence or it didn't happen.** Every dimension score comes with its line of evidence: the three
  strangers, the Before → After, the share message, the search and its date. Every research signal
  carries the date it was read.
- **Truth before aha.** An aha makes a claim feel true even when it isn't. Check the core claim; if it
  can't be checked, Click is capped and the report says so first.
- **A like is not a share.** Pleasant, broad, harmless ideas collect likes and stop. Name the like
  trap when you see it, even when the idea is charming. Kill kindly, but kill: every REWORK comes with
  three re-angles, and every KILL says what to look for instead.
- **The creator owns the idea.** In Score mode, score what was brought. Offer re-angles as options;
  don't swap in your own idea unless asked.
- **Score blind when you can.** Whoever wrote a concept will over-score it. In Run mode, the gate runs
  in a fresh subagent.
- **Honest about what is known.** The score is not calibrated against real results yet, and the 70 bar
  is a starting guess. Never predict views. Say which signal a concept should move (sends, follows,
  views ÷ subs) and stop.
- **Two scores, side by side.** The entertainment score is never added to the Hooks skill's score.

Calibration: a 7 on Share motive means a specific recipient and a message that makes the sender look
good. Most first-draft concepts score 3-5 there. If you are scoring 8+ everywhere, go back to the
anchors in `references/entertainment-rubric.md`.

## Scout mode

Read `references/research.md` first.

1. **Intake.** Ask only for what is missing: the channel (URL or description), platform (Shorts,
   Reels or both), language, audience, and what can actually be filmed or generated. With a channel
   URL, build the ledger and find the channel's own outliers:

   ```bash
   python <skill-dir>/scripts/scout.py channel https://www.youtube.com/@handle --n 50 --out research/
   ```

2. **Gather signals.** For each content pillar, find outliers and check saturation; read the
   comments on the best outliers; scan trends and Wikipedia; use WebSearch for news and checked
   oddities. Date everything.

   ```bash
   python <skill-dir>/scripts/scout.py search "topic words" --n 15 --out research/
   python <skill-dir>/scripts/scout.py comments https://www.youtube.com/shorts/ID --out research/
   python <skill-dir>/scripts/scout.py trends --geo US,GB,CA,AU
   python <skill-dir>/scripts/scout.py wiki --lang en
   ```

   Needs Python 3.9+ and yt-dlp (`pip install yt-dlp`). Only open sources are used: never sign in,
   spoof a browser or work around a bot check. Instagram has no open source; research Reels topics
   through Shorts, trends and the web.

3. **Topic board.** Collect 15-30 candidates, each with the signal that put it there. Filter on Who
   cares, Fresh and room for an aha, and keep 5-8, ranked (`assets/topic-board.md`).
4. **Concept cards.** For the best 3-4 topics, write 2-3 concepts each using the angles in
   `references/angles.md`, on `assets/concept-card.md`. Verify each card's core claim and run a
   saturation search on its core point.
5. **Rank.** Give each card a quick score, clearly labelled "not blind", and recommend Score mode in a
   fresh context (or Run mode) for the real gate.

Deliver the board and the cards as markdown files. Lead the chat reply with the top three concepts
in one sentence each, with their share message.

## Score mode

Read `references/why-people-share.md` once per session, and `references/entertainment-rubric.md` for
every scoring.

1. **Name what's being scored:** a concept (an idea in any form, or a card), a script, or a video
   (transcript, key frames and title; if a Hooks review folder exists, use its `report.md`
   transcript and contact sheets).
2. **Get the context:** platform and channel. Fresh needs evidence: run a saturation search on the
   core point when you can, or score Fresh at most 6 and mark it unchecked. Series needs the channel;
   without it, cap Series at 6.
3. **Write the three lines first:** Before → After, the share message (with recipient and motive),
   and the bigger question. If you can't write one, that dimension is already low.
4. **Score the eight dimensions** against the anchors, each with its evidence. Compute the total and
   the Aha, Share and More scores.
5. **Name the profile** (like trap, dead-end news, trivia nobody asked for, smart but cold, rage
   bait, insider hit, hit shape) and **apply the verdict rules:** KILL, REWORK or GREENLIGHT. Call
   totals within 3 of the bar borderline.
6. **Say what to do.** REWORK: three re-angles from `angles.md`, each naming the dimension it lifts
   and the score you expect. KILL: why, and what to look for instead. GREENLIGHT: the three lines the
   script must keep.
7. **Scripts get the script check** (rubric section 6): re-score, flag any drop of 2 or more, and
   check the aha line, the share line and the more pull. Verdict PASS or FIX.

Write the report with `assets/score-report.md`, in the user's language. When several concepts are
scored, add a ranked comparison table. Lead the chat reply with the verdict, the total, the three
outcome scores and the single change that would matter most.

**From a Hooks review:** when a Hooks review asks whether the topic was worth it, score the
video in video mode and report it as its own section, beside the Hooks skill's score, never added to it.

## Run mode

Read `references/pipeline.md`. In short:

1. **Intake once,** then run without asking: channel, platform, language, length, what can be
   produced, how many scripts, and whether to pause after the gate (default: no).
2. **Scout** (above) to a topic board and concept cards.
3. **Gate:** score the cards blind in a fresh subagent. REWORK at most twice per card; KILL sends the
   run back to Scout with what failed. After three Scout rounds with no GREENLIGHT, stop and report the
   near-misses. Never lower the bar to finish.
4. **Script:** hand the greenlit card to the Hooks skill's Create mode, with the angle marked as chosen
   and the aha line, share line and bigger question to keep. Without Hooks, stop at the greenlit
   concept and a beat outline, and say what Hooks would add.
5. **Script check,** blind. FIX notes go back to Hooks, at most twice.
6. **Polish:** the Hooks skill's paper review on the final script.
7. **Final package** (`assets/final-package.md`) in the project folder, with both scores side by side.

## Learn mode

After posting (about 7 days is a fair first read), collect the numbers, append a row to the ledger
in `channel.md`, and say what it suggests for the next Scout round (`references/pipeline.md`, section
7). Results stay in the user's project folder, never in this skill's files.

## References: when to read what

- `references/entertainment-rubric.md`: the eight dimensions, anchors, outcome scores, profiles,
  verdicts, the script check and video mode. Read for every scoring.
- `references/why-people-share.md`: the psychology and platform evidence behind the score, and how
  sure to be of each part. Read once per session, before the first scoring.
- `references/angles.md`: aha, share and more angles, re-angle moves by weak dimension, worked
  re-angles, and how to write a concept card. Read for Scout step 4 and every REWORK.
- `references/research.md`: sources, `scout.py` commands, how to read reach, saturation, comments and
  trends, the topic board, and platform notes for Shorts and Reels. Read for Scout.
- `references/pipeline.md`: the full run, the project folder, blind scoring, the Hooks hand-off,
  stop rules, the final package and the Learn step. Read for Run and Learn.
- `assets/`: `topic-board.md`, `concept-card.md`, `score-report.md`, `channel.md` and
  `final-package.md`, the output skeletons.
