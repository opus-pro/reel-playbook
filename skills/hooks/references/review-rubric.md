# Review rubric

## Contents
1. Severities
2. The nine dimensions (weights, checks, anchors)
3. Verdict rules
4. Evidence format
5. Diagnose: from analytics to frames

---

## 1. Severities

| Severity | Meaning | Rule of thumb |
|---|---|---|
| **BLOCKER** | Many viewers will leave because of this before seeing anything else, or the video breaks its own promise. | Fix before posting. Usually sits in the first second, or is a missing payoff. |
| **MAJOR** | A specific moment where attention clearly drops, or a structural weakness in the hook, story or ending. | Fix in this edit. |
| **MINOR** | Polish. Real, but each one only costs a little. | Fix if cheap. |
| **NIT** | Taste. | At most three, or none. |

Each auto-flag already carries a severity. You can raise or lower it, but say why. For example,
LONG_HOLD drops to NIT when the hold is a continuous action the viewer is waiting on.

Common judgment calls:
- **First frame with no text, no context cue and an unknown face** (a stranger or an AI host): MAJOR.
  It becomes a BLOCKER when the first 3 s also add no stakes, no text and no visible change, because
  a muted viewer is then given nothing at all.
- **A face the audience already knows** (see "Channel context" in SKILL.md) is a context cue in
  itself, so it is not the MAJOR above. A clear face with a readable expression can carry frame 1
  without text, though an object or one word beside it still helps strangers.
- **The promise is not kept** (the hook or a line promises an answer the video never gives): BLOCKER.
- **A signpost line in a short** ("today let's look at", "first, the idea itself"): MAJOR when it
  sits in the first 5 s or delays the payoff, MINOR otherwise.
- **A rehook the video never pays off** ("but wait" followed by nothing new): MAJOR. It is a broken
  promise in miniature, and it teaches viewers to ignore the next one.
- **A stretch past the rehook limit with nothing said or shown** (REHOOK_GAP, about 10 s in a short):
  MINOR. Make it MAJOR when the retention graph drops there, or when it covers most of the middle.

## 2. The nine dimensions

Score each from 0 to 10, then weight. The weights put most of the score where most viewers are lost.

| # | Dimension | Weight |
|---|---|---|
| 1 | First frame | 20 |
| 2 | Hook (0-3 s) | 20 |
| 3 | Story and promise | 15 |
| 4 | Mechanism and middle | 10 |
| 5 | Pacing and transitions | 10 |
| 6 | Language and readability | 10 |
| 7 | Ending and loop | 10 |
| 8 | Sound | 3 |
| 9 | Technical and platform fit | 2 |

Total = sum of (score / 10 x weight), out of 100.

### 1. First frame (20)

**Measured:** FIRST_FRAME_BLACK, FIRST_FRAME_FADE_IN, FIRST_FRAME_STRAY, brightness, letterboxing.
**By eye:** the cold read sentence, the small, squint and safe-zone views.

- Is it a real, finished image, not black, a fade, a logo or a transition frame?
- Can a muted stranger say what it is in one glance? Is there one dominant subject?
- Is there a context cue (a place, a brand, a recognisable object) and a curiosity gap (a number, a
  contrast, an odd situation)?
- Is the text big, three words or fewer, and outside the UI zones?
- Is the face a draw or a cost? Use the channel context. A face much of the feed recognizes (the
  creator's face is the brand and the channel has millions of subscribers, or the user says the
  audience knows it) works like a logo: frame 1 can reach 6-7 on that face, a readable expression and
  one cue. A stranger's face (a new or small channel, an AI host) needs an object, a number or text to
  reach 6. With no channel context, score the face as a stranger's and say the score would rise by
  about 2 if the audience knows it.

Anchors: **0-3** black, faded, stray or meaningless; or a talking head with no context. **4-6** clear
subject, but no reason to stay, or the text is small, cluttered or under the UI. **7-8** one subject,
one context cue, one hook word or number, readable small. **9-10** a poster you would stop for, with
the question obvious at thumbnail size.

### 2. Hook, 0-3 s (20)

**Measured:** LATE_AUDIO_START, LATE_FIRST_WORD, HOOK_STATIC, HOOK_LINE_LONG, FILLER_PHRASE in the
first 5 s, DARK_OPENING; the words spoken in the window.
**By eye:** the hook sheet, muted and then with the transcript.

- Is the hook said within about 2 s, and does it contain stakes (a why), not just the topic?
- A story opener ("Two years ago, a stranger at the airport gave me this note") opens a gap without naming stakes: a
  specific person and a past moment that clearly lead somewhere. Count that as a gap, not as a topic.
  It still needs the stakes named within about 5 s; if they come later, the hook stays at 4-6.
- Does the picture preview the payoff (J-cut: the voice states the premise over a payoff shot)?
- Does a muted viewer get the premise from the picture and text by 3 s?
- Is there zero throat-clearing: no greeting, name, "in this video" or "let's get started"?
- The first-second cut test: would the video lose anything if its first 10 frames were gone?
- Which hook family is it, and does another family suit this payoff better (`hooks-and-rehooks.md`)?

Anchors: **0-3** no hook in 3 s, or filler or silence first. **4-6** the topic is stated but has no
stakes, or the hook needs sound to work. **7-8** stakes are stated fast and the picture supports them.
**9-10** stakes plus a payoff preview, and it works muted.

### 3. Story and promise (15)

**By eye and transcript:** the story spine.

- Who wants what, because why, under what constraint? Does the payoff answer the hook's exact
  question?
- Is the promise kept? A clickbait gap (the hook promises X, the video delivers Y) is a BLOCKER even
  if every frame is beautiful.
- Is the premise broad enough? Would someone outside the niche care? Is there a zoom-out available?

Anchors: **0-3** a topic with no stakes, or a broken promise. **4-6** stakes exist but are vague or
arrive late. **7-8** a clear spine, stated early, with the promise paid. **9-10** a spine that a
10-year-old could retell, with a payoff that is visual and surprising.

### 4. Mechanism and middle (10)

**Measured:** LONG_HOLD, STATIC_STRETCH, FROZEN_PICTURE, REHOOK_GAP, the visual change count and
longest hold, the rehook candidates, and seconds with a low `change` value and no words.
**By eye:** the timeline sheets and the rehook map.

- The skip test: if you watched only the last 3 s, what would you lose?
- Is there a device (shrinking constraint, comparison, steps, a counter, a bet) that makes the
  process matter?
- The rehook map: does every seam close one question and open the next, about every 5-8 s? Is each
  rehook specific, paid off by the next beat, varied in form, and visible with the sound off?

Anchors: **0-3** a fixed process; skipping to the end loses nothing. **4-6** something happens, but no
escalation, and the seams open nothing new. **7-8** a clear mechanism with steps, and a rehook at most
seams. **9-10** escalation, where each beat raises the stakes of the payoff and every seam opens the
next question.

### 5. Pacing and transitions (10)

**Measured:** cuts per 10 s, shot lengths, FLASH_FRAME, GRADUAL_TRANSITION, BLACK_MID, brightness
jumps at cuts.
**By eye:** every row of the cut sheets, using `transitions.md`.

- Does every cut have a reason, land on a word, beat or action, and keep the eye-trace?
- Are there any accidental frames, soft dissolves or dead holds?
- Is the visual change cadence right for the content?

Anchors: **0-3** errors (flash frames, black gaps), or a single long hold with nothing changing.
**4-6** cuts exist but feel arbitrary, or a few land mid-word or mid-action. **7-8** cuts are
motivated and tight. **9-10** cuts are invisible because they ride the action and the words, and
there is at least one match cut.

### 6. Language and readability (10)

**Measured:** FK grade, hard words, number density, fillers, speech rate.

- Could a 10-year-old follow every line the first time, with nothing that needs a pause or
  reference?
- Does every line raise a question or answer one? Lines that only connect or announce get cut.
- Are the numbers few, small and concrete?

Anchors: **0-3** jargon-heavy, grade 9 or higher, or full of filler. **4-6** clear, but with dense
numbers or long sentences. **7-8** short, plain lines. **9-10** a child could retell it, and every
line pulls.

### 7. Ending and loop (10)

**Measured:** TAIL_DEAD_TIME, TAIL_AFTER_LAST_WORD, FADE_TO_BLACK_END, AUDIO_FADES_OUT,
ENDING_LINE_LONG, loop SSIM.
**By eye:** the tail sheet and the loop seam sheet.

- Does it end on the payoff, abruptly, within a beat of it?
- Is there no outro, no subscribe ask, no fade and no music tail?
- Does the last moment flow back into frame 1, as a visual match, a sentence loop or a sudden cut?

Anchors: **0-3** an outro, a fade or a dead tail. **3-4** abrupt with a clean seam, but there is no
payoff to land on: an abrupt ending only works when it cuts on the answer. **4-6** it ends on the
payoff but lingers. **7-8** an abrupt ending on the payoff. **9-10** abrupt, and the seam makes the
replay feel like part of the video.

### 8. Sound (3)

**Measured:** LUFS, true peak, DEAD_AIR, LATE_AUDIO_START. Sound starts on frame 1, there are no
gaps under a voice-over, and the level is near -14 LUFS. You cannot hear the music, so do not judge
it beyond levels and gaps unless the user describes it.

Anchors: **0-3** silent stretches or digital silence (below about -60 dB) inside the video, or a late
start. **4-6** levels are fine, but there are repeated gaps over ~0.5 s between lines. **7-8** tight
delivery and levels near -14 LUFS, with at most one short gap. **9-10** no gaps, sound on frame 1,
and sound carrying the cuts (J- and L-cuts, hits on the edit points).

### 9. Technical and platform fit (2)

**Measured:** NOT_VERTICAL_9x16, BELOW_1080P, LETTERBOXED, DECODE_MISMATCH. Also, by eye, captions
and text inside the safe zones.

Anchors: **0-3** wrong aspect, letterboxed, or decode errors. **4-6** 9:16 but below 1080p, or text
under the UI. **7-8** 1080x1920 and clean, with captions present. **9-10** all of that, plus captions
and text placed for every platform's safe zones.

## 3. Verdict rules

Pick exactly one. Work down the table and take the first one that applies:

| Verdict | When |
|---|---|
| **RETHINK** | The story or the promise has to change: there is no story spine, or the hook promises something this video does not deliver. This applies even when every piece needed for the new version already exists. Go back to the wrappers in the playbook. |
| **RESHOOT** | The story is right, but a fix needs a shot or recording that exists nowhere in the project, such as no payoff shot to preview, or no usable first frame. |
| **RE-EDIT** | The story is right and the fixes use material that already exists: trims, reorders, a new first frame taken from existing shots, text, captions, re-recorded or regenerated lines. |
| **POST** | No BLOCKER, and the total is at or above the channel's bar (below). If a MAJOR remains in dimensions 1-3, say "POST after fix 1" and name the fix. |

"Material that already exists" means anything in the project, not only what is in this cut: unused
takes, the long-form recording, generated assets. When RETHINK is cheap because the material exists,
say so in the verdict line ("RETHINK, cheap: every line needed is already recorded").

A BLOCKER anywhere rules out POST, whatever the score. State the verdict in one line, followed by
the reason in one sentence.

### The channel's bar

| Total | New channel (the feed doesn't know you yet) | Established channel (the audience knows the face or brand) |
|---|---|---|
| **80+** | At the bar: POST | Above the floor: POST |
| **70-79** | Below the bar: apply the top fixes to reach 80 | At the floor: POST |
| **Below 70** | Well below the bar | Below the floor: likely to stay with the existing audience |

- **Borderline.** Totals repeat within about ±2 points between blind reviews, so a total within 2
  points of the bar (68-72, 78-82) is borderline. Say so in the verdict line, then either apply the
  top fix or average two more blind reviews before deciding.
- **No channel context?** Use the new-channel bar (80) and say which bar you used.
- **Where the bars come from.** A calibration on 14 Shorts (November 2026) compared Hooks grades
  with views ÷ channel subscribers. Every Short graded 70 or more got more views than its channel has
  subscribers; most below 70 did not. The sample is small and all from
  established channels, so the 70 floor has some evidence and the 80 bar for new channels is a
  target, not a measured line. See "Calibration so far" in `method.md`.

## 4. Evidence format

- A single point: `[00:01.20 f29]`, with the time as shown on the tile label and the frame index.
- A range: `[00:12.00-00:14.03]`.
- A measured value: `(FK grade 11.2)`, `(silence 0.84 s)`, `(scene 0.62)`.
- Cut log rows refer to the cut number in `report.md`: `cut #4 [00:07.13 f171]`.

## 5. Diagnose: from analytics to frames

| What the analytics show | Most likely cause | Look at |
|---|---|---|
| Viewed vs swiped well below the channel's usual (about 70% is common) | Frame 1, or the first half-second of sound | `first_frame*`, the first row of the hook sheet |
| Steep drop in the first 3 s of the retention graph | The hook has no stakes, there is filler, or no preview, or the frame 1 promise does not match what follows | hook sheet + transcript of the first 3 s |
| A steady slide through the middle | No mechanism, no rehooks | timeline sheets, `seconds.csv`, the rehook map |
| A drop right after a beat resolves | The answer closed the loop and nothing opened the next one: a missing, generic or late rehook at that seam | the rehook map, plus `--span` around the seam |
| A cliff at one specific second | Something at that moment: dead air, a confusing cut, a long hold, a topic shift | `--span` of 1 s either side of the cliff |
| A drop in the last 1-2 s | A dead tail, sign-off or fade | tail sheet. Trim it in Studio, the cheapest fix there is. |
| Average viewed above 100% | Replays: the loop works | Protect the ending in any re-edit. |
| High viewed rate, low average viewed | The first frame overpromises, or the payoff is weak or late | story spine, the promise vs the payoff |
| Average viewed fine, views still low | Narrow premise; nobody outside the niche cares | the zoom-out and doubter wrappers in the playbook |

Ask for the retention graph's timestamps and say which frame sits at each drop. Never guess at
analytics the user did not show.

**Comparing performance across Shorts or channels.** Use views ÷ channel subscribers, not raw views,
because raw views mostly measure channel size. At about 1× or less, the Short stayed with the existing
audience. At about 3× or more, it reached people who don't subscribe. Subscriber counts change over
time, so note when they were taken.
