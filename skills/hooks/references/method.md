# The Hooks method

The principles behind every review and brief: what each one says, why it works, how to check it, and
how sure to be of it.

## Where this comes from, and how much to trust it

The core is Jenny Hoyos's short-form practice. She is a US creator who drew hundreds of
millions of Shorts views in 2023, reportedly averaging more than ten million per Short. She makes
original, high-polish Shorts rather than clips cut down from long videos. Her practice reached us
second-hand, through a Chinese-language breakdown by the Taiwanese creator Joeman, which added his
own cases.

Weigh it accordingly:

- **The mechanics last.** Story over topic, designing the first frame, simple words, a mechanism in
  the middle and an abrupt ending all follow from how people scroll, and none depends on an
  algorithm setting.
- **The exact numbers are hypotheses.** "33-34 seconds", "95% completion" and "over 100% under 30
  seconds" are one channel's observations from around 2023, and YouTube has changed since. Shorts can
  run up to 3 minutes (since late 2024), and in 2025 YouTube began counting every play and replay as a
  Short view, keeping the older measure as "engaged views". Test the numbers against the user's own
  analytics before treating them as targets.
- **Lines marked *Practice*** are common short-form editing craft, not from the source. Hooks
  adds them because a frame-level review needs them.
- **The hook bank and rehooks** (`hooks-and-rehooks.md`) draw on two more practitioner sources: a
  Socialmon guide to Reels hooks, and Marquise Peters' video on rehooks (December 2025). Both are
  advice from experience, not studies. Their numbers, such as rehook intervals and attention spans,
  are claims to test.

---

## 1. Story beats topic

**Rule.** A topic is a subject. A story is someone who wants something, for a reason, against a
constraint, while we wait to see whether they get it.

> WHO wants WHAT, because WHY, but CONSTRAINT. Will they? (The payoff is the reveal.)

**Examples from the source, paraphrased:**
- "How much money can I make cooking?" is a topic. "My kitchen broke, so I have to cook my way to
  the repair money" is a story: there is a goal, a reason and a finish line.
- "What does $5 buy?" is a topic. "Grandma thinks Christmas gifts cost too much, so I'm getting her
  a $5 gift to prove a cheap gift can still be a good one" was her most-viewed Short. Viewers stay
  for Grandma's reaction.
- Joeman's phone unboxings and his "a PC editor switches to Mac" video stayed flat despite heavy
  testing and scripting. They had no stakes, and the audience was narrow.
- His Huawei vs iPhone video worked because it opened on the chip and trade war: can Chinese tech
  break the blockade? People who never watch phone reviews cared about that question. Zooming out
  from a niche to a bigger world question widens the audience.
- For knowledge channels, the model is opening on a world event and its underlying logic, as the
  finance channel Xiao Lin Shuo does every time. That makes dry subjects watchable.

**Why it works.** Stakes make the viewer predict, and a viewer who is predicting stays to check the
prediction. A topic gives them nothing to predict.

**How to check.** Fill in the story spine (who, wants, because, constraint, mechanism, payoff). Any
empty slot is a finding. Then try the one-breath test: can a 10-year-old retell the premise in one
sentence?

## 2. The first frame decides the swipe

**Rule.** Design frame 1 as a poster. It, not "the first two seconds", is what moves the share of
people who stay.

- YouTube Studio reports **viewed vs swiped away** for each Short. Joeman's channel sat around
  68.5-69%, which he described as typical (about 70%). Jenny's sat around 85%.
- She sketches the opening frame on an iPad before filming, like a storyboard.
- In her "$1 version of a fast-food signature dish" series, frame 1 had the food dead center, the
  restaurant's sign directly above it, and "$1" across the middle. Her face was not in it. Food and a
  famous logo pull in strangers better than a creator's face, which only fans recognise.

**Why it works.** In the feed, frame 1 shows before any sound and before any motion has registered.
The decision to stay is made on a still image.

**How to check.** Cold read `first_frame.png` muted: what is it, and why stay? Check that it is
readable at small size, that one shape dominates in the squint view, and that nothing important is
under the app UI. A black frame, a fade-in, a stray frame from another shot, a logo card or a blurry
transition frame at frame 0 is a BLOCKER.

**Composition rules (Practice):** one subject, center-weighted in the middle band of the screen, high
contrast against the background. Add one context cue (a logo, a place, a recognisable object) and at
most three words or one number of text. It must be readable with the sound off.

## 3. The first three seconds: say the hook, show the payoff

**Rule.** Run two tracks at once. The voice states the hook within about 2 seconds while the picture
jumps ahead to the payoff as a preview, then cuts back. In the $1 series, the voice says the premise
while the picture shows the family blind-tasting the $1 burger, a moment from the end.

**Muted viewers.** Many people scroll with the sound off, so the picture and on-screen text alone must
carry the hook for the first 3 seconds.

**How to check.** The hook sheet shows 0-3 s at 10 frames per second. Read it muted first, then
with the transcript. Measured checks: the first word lands at or before about 0.5 s, sound starts on
frame 1, and the picture visibly changes in the first 1.5-3 s.

## 4. Write for a 10-year-old

**Rule.** Use the simplest words that carry the idea.

- She pulled the captions of thousands of popular Shorts and ran them through English readability
  tests. To get the captions, she changed `/shorts/` to `/watch?v=` in the URL to reach the desktop
  page, then used an extension to extract them. The bigger the hit (MrBeast, for example), the simpler
  the words.
- She swaps "business finance" for "making money".
- She tests ideas by talking them through with a young child, and builds premises on amounts a child
  handles: $1, $5.
- Joeman adds that adults scrolling don't want to think either, so scripts should drop jargon
  and obscure theory. His caution: making only simplified content for a long time can burn a creator
  out.

**How to check.** Aim for Flesch-Kincaid grade 5 or below, avoid unexplained terms, and use small,
concrete numbers. Keep it to roughly one number per beat. `scripts/readability.py` measures all of this.

## 5. Engineer retention, then let the data correct you

- **Volume is data.** Posting a lot raises the odds of a hit and builds up analytics to learn from.
  One of her Shorts had under 100k views after five days. Its retention graph showed a sharp drop in
  the final second. She trimmed that second in Studio, completion rose from 83% to 88%, and the Short
  went on to about 18 million views.
- **Length.** She observed that a Short under 30 s needed an average view of over 100% (rewatches)
  to break out, while above 30 s about 95% was enough for ten-million-level distribution. So she cut
  to 33-34 s. Treat this as a hypothesis (see the top of this file).
- **The abrupt ending.** Her viewed rate was about 85%, but her average percentage viewed was about
  95%, so many people watched more than once. Part of that is how short the videos are. Part of it is
  deliberate: she ends very abruptly. A blind-test verdict is one or two words, then it's over. By the
  time the viewer thinks "wait, that's it?", the video is already playing again.

**How to check.** The video should be silent or dead for no more than about half a second after the
last meaningful moment. The last line should be very short, with no sign-off, no subscribe ask, no
fade to black and no music tail. Look at the loop seam: last frames, then first frames.

## 6. Give the middle a mechanism

**Rule.** A mechanism is a device that makes the process worth watching, so viewers cannot skip to
the end.

- MrBeast's "last to leave the shrinking circle wins": the shrinking circle is the mechanism. If the
  circle stayed the same size, viewers would skip to the winner.
- Scratch-off tickets: buying NT$2,000 of tickets and scratching them is a fixed process, so people
  skip to the result, or just read the news story instead. Joeman's fix gave each staff member the
  same budget to spend on any mix of ticket prices. Comparing which choice paid back best gave the
  process tension.
- "3 steps to ...": if step 1 is good, people stay for steps 2 and 3.

**How to check (the skip test).** If a viewer watched only the last 3 seconds, would they lose
anything? If not, the middle has no mechanism. Then map the rehooks: at every seam where a beat
resolves, something should close that beat's question and open the next one. In a short that is
about every 5-8 seconds, said or shown. A mechanism makes rehooks easy, because each step, round or
counter update is a natural seam. Types, timing and faults are in `hooks-and-rehooks.md`.

## 7. Zero filler

**Rule.** "Without further ado, let's get started" is itself the filler. So are greetings, channel
intros, "in this video" and "today we're going to". Cut straight into the content.

**How to check.** `readability.py` and the analyzer flag known filler phrases. Read the transcript
for others, because any line that only announces what is coming is filler.

## 8. Copy the craft, not the topics

Cheap, formulaic premises ($1 meals, $5 gifts) attract copycats and wear out. What transfers is the
craft: the rhythm, the first-frame design, the first-3-second structure and the habit of reading the
data. When suggesting premises, do not clone hers. Use the wrappers in the playbook to find a story
that is native to the user's topic.

---

## Practice that Hooks adds

These are common in short-form editing and not from the source. They help with frame-level judgment.

- **Visual change cadence.** In narrated shorts, something visibly changes every ~1.5-3 s: a cut, a
  punch-in, b-roll, or text popping on. More than about 3 s with no change needs a reason, such as
  the action itself carrying the shot.
- **Cut on action and on words.** Cuts land on a movement, a beat or the end of a word, never in the
  middle of one.
- **Eye-trace.** Keep the subject in the same screen area across a cut unless the jump is the point.
  Every jump makes the eye search for a moment.
- **J- and L-cuts.** Let audio lead or trail the picture to carry momentum across cuts. This is how
  the hook voice-over runs over the payoff preview.
- **Safe zones.** Feed apps cover roughly the bottom quarter (title, channel, audio) and a column on
  the right (buttons), plus a strip at the top. Keep the subject and the text out of those areas.
- **Sound.** Deliver near -14 LUFS integrated with true peak at or below -1 dBTP. Burned-in captions
  serve muted viewers.

### AI hosts

- **A generated face is a stranger's face.** It has no fans, so in frame 1 it costs attention rather
  than drawing it. Lead with an object, a number or text, and let the host earn the face later.
- **Check the artifacts where they hurt most.** Look at every frame of the first second (`--span
  0-1`) and of the payoff line: lip shapes on rounded vowels, half-closed eyes, teeth and hands. An
  odd expression in the poster window reads as an attitude the script never meant.
- **Chained clips reset.** Clips generated from one reference image often start and end on the same
  pose. See "reset joins" in `transitions.md`.
- **Disclosure.** Platforms ask creators to label realistic synthetic people or voices (YouTube calls
  this altered or synthetic content). Mention it when the host is realistic. It is the user's call,
  and the rules change, so do not state them as fixed.

---

## Calibration so far

The first check of the Hooks skill's grades against real results, November 2026. Eight published Shorts
from established channels were graded blind (no view counts, no hint which were hits): six channel
hits and two same-channel controls. The performance index is views ÷ the channel's subscribers.

What it suggests:
- **A floor near 70.** Across 14 Shorts, every Short graded 70 or more got more views than its
  channel has subscribers; 5 of the 8 below 70 did not. Reach below 70 varied widely, and a few Shorts
  went far past their subscriber count anyway, so below 70 means riskier, not dead.
- **Repeatable grades.** Three blind runs of the same Short gave totals within 3 points (SD ≤ 1.7),
  dimension scores that moved by 1 at most, and mostly identical rehook calls.
- **Known misses.** Some hits grade below their reach, and one same-channel pair ordered the wrong
  way. The grade measures the craft of the telling, and a strong subject can beat a plain opening.

Limits: 14 Shorts, all from established channels and leaning towards hits, graded by one model, and
subscriber counts taken at review time rather than at upload. The rank correlation between grade and
reach was about 0.36. Treat the bars in `review-rubric.md` as working hypotheses, and recalibrate on
the user's own Shorts: grade before posting, record views ÷ subscribers after a week.

The Shorts themselves and their scores are kept outside the skill, in `docs/hooks-calibration.md` in this repository, so a blind review can't see the answers.
