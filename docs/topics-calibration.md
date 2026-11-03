# Calibration log

How the Topics skill's entertainment score compares with what real shorts did. This file lives outside
the skill on purpose: scorers read the skill folder, and a blind test only works if the answers are
not in it. Do not copy video names, scores or reach figures into `skills/topics/`.

**Status (2026-11-02): not calibrated.** The weights and the 70 bar are a reasoned starting point.

## Signals

| Score | Real signal | Where it's public |
|---|---|---|
| Total | views ÷ channel subscribers (about 1x or less: stayed with the audience; about 3x or more: reached strangers) | YouTube via `scout.py`; TikTok and Instagram pages |
| Share | shares ÷ views, and shares ÷ likes (low shares per like is the like trap) | TikTok pages; Instagram Insights for the creator's own reels |
| More | subscribers or follows gained per 1,000 views | Only in the creator's own analytics |
| Like trap | high likes ÷ views with low shares ÷ views | TikTok |

YouTube hides share counts, so YouTube videos calibrate the total only.

## Plan for round 1

1. **Same-channel pairs.** Pick channels in four niches (fun facts, event commentary, explainers,
   odd places or animals). For each, a hit (views ÷ subs well above the channel's usual) and a control
   in the same format at about the same time. Same channel and format holds execution roughly
   fixed, so the gap between them should be the topic. The Hooks skill's round 1 could not separate such a
   pair (70 vs 68 on an 8x reach gap); this score should.
2. **About 20 videos (10 pairs),** taken from YouTube Shorts via `scout.py channel`, plus a TikTok set
   with public share counts for the Share score. Record views, subscribers and shares with the date.
   Downloaded videos go in the git-ignored `calibration/` folder.
3. **Blind and execution-free.** Agent A watches each video and writes a neutral concept card: the
   premise and the payoff, no hook wording, no channel name, no numbers. Agent B scores the card with
   the rubric, never seeing views or which video is the hit. A second set of agents scores the videos
   in video mode, for comparison.
4. **Report:** pair ordering (does the hit outscore its control?), Spearman correlation of the total
   with views ÷ subs and of Share with shares ÷ views, and repeatability over 3 blind runs (spread of
   totals and of verdicts).
5. **Combined:** does the entertainment score plus the Hooks skill's score predict reach better than
   either alone?
6. **Each scorer reports** whether anything it read gave away the answer. The Hooks skill's first
   post-fix re-test was voided for exactly this.

## Results

None yet.

## Eval observations (not calibration)

- **2026-11-02, first eval run** (one run with the skill, one without, per case). The dog-mayor
  concept, the kind of idea this design treats as a hit shape, scored 64 and got REWORK: Fresh 4,
  because the story is widely covered, and 6 or 7 on everything else. With Fresh at its unchecked
  cap of 6 it would still be 66. That is a reasonable verdict for a well-worn story, so the eval now
  accepts it. But if round 1 finds real hits scoring in the 60s, the anchors or the 70 bar are too
  strict. One run is not evidence either way, so the rubric is unchanged.
