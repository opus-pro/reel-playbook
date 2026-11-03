# Calibration log

How the Hooks skill's grades compare with what real Shorts did. This file lives outside the skill on
purpose: reviewers read the skill folder, and a blind test only works if the answers are not in it.
Do not copy Short names, grades or reach figures back into `skills/hooks/`.

The performance index is **views ÷ the channel's subscribers**. Raw views mostly measure channel size.
At about 1× or less a Short stayed with the existing audience; at about 3× or more it reached
non-subscribers.

## Round 1, November 2026: eight Shorts, graded blind

Six channel hits and two same-channel controls (a lower-performing Short in the same format, from the
same channel, at about the same time). Each reviewer saw the video, the analyzer's measurements and
the auto-captions, never the view count or which Shorts were hits. Views and subscribers were taken on
2026-11-01.

| Short | Grade | Views | Subscribers | Views ÷ subs |
|---|---|---|---|---|
| Jenny Hoyos: What's Faster: Drive Thru or Cooking? | 78 | 107M | 12.4M | 8.6× |
| Jenny Hoyos: I Built a Secret Room with $0 | 74 | 185M | 12.4M | 14.9× |
| Nick DiGiovanni: 1 Second vs 1 Hour Chicken | 70 | 130M | 48.1M | 2.7× |
| Nick DiGiovanni: 1 Second vs 1 Hour Egg (control) | 68 | 16.5M | 48.1M | 0.34× |
| Jenny Hoyos: $1 Burrito vs Chipotle (control) | 68 | 53K | 12.4M | 0.004× |
| MrBeast: Hit The Button, Win $1,000 | 60 | 662M | 524M | 1.3× |
| Ryan Trahan: Surprising the kid who wrote me this letter | 56 | 173M | 24.1M | 7.2× |
| Joeman: Tesla Roadster order (not in English) | 48 | 1.4M | 2.86M | 0.48× |

- Every Short graded 70+ reached at least 2.7×; most below 70 stayed at or under about 1×.
- Both hit/control pairs ordered correctly, but narrowly: 74 vs 68 (Jenny) and 70 vs 68 (Nick).
- Spearman rank correlation between grade and views ÷ subs: 0.50 (n = 8).
- The Joeman Short had no usable transcript (YouTube's captions came from an English AI dub), so its
  language and rehook timing were read from burned-in captions.

## Repeatability

Three blind runs each, same brief, identical analyzer output for runs 2 and 3:

| Short | Run 1 | Run 2 | Run 3 | Spread |
|---|---|---|---|---|
| Chicken | 70.3 | 67.3 | 70.3 | 3.0 |
| Egg | 68.0 | 66.0 | 68.0 | 2.0 |
| Ryan Trahan | 55.5 | 55.3 | 55.5 | 0.2 |

Dimension scores moved by at most 1 point. Hook calls were identical; rehook calls mostly matched
(Egg identical; Chicken 6 shared, run 1 added 2; Ryan 5 shared, run 2 swapped one for two others).
Conclusion: totals are good to about ±2 points, so the rubric's bars use a ±2 grey zone.

## Fixes made from round 1

- A known creator's face is now scored as a draw, using the channel context Review mode asks for.
- A "story opener (callback)" hook family was added for openings like "One year ago, …".
- Grade bands: 80 for a new channel, 70 for an established one, ±2 borderline.

Still scored as flaws, on purpose: the Ryan Trahan Short's late stakes (about 18.8 s) and its
dance-and-comment outro. It may have succeeded despite them. Two hits (MrBeast, Ryan Trahan) end on a
call to action (subscribe, comment); watch whether that pattern holds before changing the ending rules.

## Lesson: keep the test set out of the skill

The first post-fix re-test was void. The skill's reference files had been updated with this round's
table and with an example close to the Ryan Trahan Short's opening line, and the reviewers read them
before scoring (two of three reported it). The results (Chicken 73.3, Egg 68.0, Ryan 63.0) were set
aside, the skill was cleaned, and the re-test was run again. Each re-test reviewer was also asked to
report whether anything it read gave away the answer.

## Re-test after the fixes (clean, blind)

Channel context given as Review mode now asks for it (subscribers, established, face known).

| Short | Before (mean of 3) | After | What moved | Bar (established: 70) |
|---|---|---|---|---|
| Ryan Trahan | 55.4 | 63.0 | first frame 4→6, hook 5→6, story 6→7 | below |
| Chicken | 69.3 | 73.3 | first frame 5→6, language and ending about +1 | POST |
| Egg (control) | 67.3 | 68.0 | nothing | borderline below |

- The fixes did what they were meant to: the known-face rule and the story-opener family lifted the
  Short they were built for, and the control in the threshold pair stayed put, so the hit/control gap
  grew from 2 to about 5 points, either side of the 70 floor.
- Ryan Trahan still grades below the floor. The rest of the gap is late stakes and the outro, which the
  rubric still counts as flaws.
- Only three Shorts were re-graded. MrBeast, Joeman and Jenny Hoyos's Shorts were graded under the old
  face rule; a full re-grade of all eight is needed before recomputing the correlation.

## Round 2, November 2026: six more Shorts, graded blind

Five new channels were picked by hand, one per niche, and all are large. A fixed rule then chose a pair
from each: within the channel's latest 50 Shorts, skipping the newest 5, the hit has the most views, and
the low performer has the fewest views among the 10 uploads nearest the hit. Ten Shorts were picked, and
six were graded, because only those six copies were supplied. Views and subscribers are rounded public
counts taken on 2026-11-03.

One reviewer per Short saw the analyzer's measurements, a Scribe transcript and the channel context, never
the view count or which Short was the hit.

| Niche | Short | Role | Grade | Verdict | Views | Subscribers | Views ÷ subs |
|---|---|---|---|---|---|---|---|
| Money | Mark Tilbury: HATER CHALLENGES MILLIONAIRE (to sell a pen) | Hit | 76 | Post after fix | 27M | 9.34M | 2.9× |
| Money | Mark Tilbury: I Bought The Same Items in NYC | Low performer | 61.7 | Re-edit | 888K | 9.34M | 0.095× |
| Cooking | Max the Meat Guy: YouTubers Season My Steak… | Hit | 73 | Post after fix | 144M | 10.4M | 13.8× |
| Explainer | Zack D. Films: Why Dobermans Have Cropped Ears | Hit | 71.8 | Post, borderline | 36M | 29.5M | 1.2× |
| Science | Nick Uhas: I got stung so bad! | Hit | 62.7 | Re-edit | 34M | 1.06M | 32× |
| Science | Nick Uhas: When will explode? | Low performer | 65 | Re-edit | 11K | 1.06M | 0.01× |

- The money pair ordered correctly by 14 points.
- **The science pair ordered the wrong way.** This is the biggest miss in the log: the rubric marked down a
  plain first frame and a slow start on a Short that reached 32× its subscribers, while its low performer
  graded 2.3 points higher.
- Not graded: the low performers for cooking and explainer, and both comedy Shorts (Alan Chikin Chow), so
  this round has four hits and two low performers.
- Spearman rank correlation between grade and views ÷ subs for this round: 0.26 (n = 6).

Limits of this round:

- The copies were low-resolution re-encodes: five at 360 x 640 and one at 202 x 360. Reviewers were told to
  ignore this, but it may still have affected first-frame judgments.
- Blinding wasn't perfect. One reviewer recognised the creators, and another read the channel name on a
  prop in the video. One noted that the skill's mention of a calibration hit that used a story opener could
  hint at the result for a Short with that opening, so those lines were then removed from the skill.

## All 14 Shorts together

| Grade | Shorts | Median views ÷ subs | More views than subscribers |
|---|---|---|---|
| 70 or higher | 6 | 5.75× | 6 of 6 |
| Below 70 | 8 | 0.41× | 3 of 8 |

- Every Short graded 70+ got more views than its channel has subscribers; 5 of the 8 below 70 did not.
- Spearman rank correlation between grade and views ÷ subs: 0.36 (n = 14).
- This combines rounds with different conditions. Five round 1 grades came before the rubric's fixes, and a
  full re-grade still needs those video files. The sample leans towards hits from large channels, so it
  says little about small channels.
