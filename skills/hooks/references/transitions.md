# Judging cuts and transitions

A short has no time to recover from a bad cut. Each one either carries the viewer forward or gives
them a moment to leave. This file covers how to judge every cut on the cut sheets and what each kind
of transition costs.

## Reading the sheets

- `sheets/cuts_NN.png` has one row per edit point: **[two frames before | two frames after]**. Each
  tile is labelled with its time (`00:00:07.133`) and frame index (`f214`). The edit-point table in
  `report.md` gives each one's number, kind, time, scene score, sheet and row. Kinds:
  - **cut**: a hard cut.
  - **jump**: a one-frame jolt below the cut threshold. In a talking head this is a jump cut. In
    generated video it is a hidden join between clips. In motion graphics or animation it is an
    element snapping on or off, such as a caption swap or a pose snap. Jumps scoring above about 0.1
    are often real cuts between similar angles. Judge each one on the sheet. Caption swaps are worth
    checking against the words: does the caption change on the word, and does it stay long enough to
    read?
  - **given**: an edit point you passed with `--edits`.
- `sheets/transitions_NN.png` has one row per soft transition (dissolve, fade, whip): the frame
  before it starts, two frames inside it, and the frame after it ends.
- For frame-accurate questions (is that one stray frame? where exactly does the word end?), rerun
  with `--span START-END` and look at every frame.
- `frames.csv` has the numbers: `scene` (cut strength), `yavg` (brightness), `ydif` (motion), and
  `crop_*_pct` (picture area).

## The per-cut checklist

Answer these for every edit point. Then give it one verdict: **KEEP**, **TRIM n frames**, **TRIM
AROUND** (keep the join, cut the dead hold on either side), **MOVE to t**, **REPLACE with ...**, or
**REMOVE**.

1. **Reason.** Why does the cut happen here? Good reasons are new information, a word or beat
   landing, an action continuing, a reaction, a payoff preview, or a rehook (cut on its turn word,
   such as "but" or "then"). If it has no reason, the cut is noise. Cut the shot or move the cut.
2. **Timing.** Does it land on a word boundary, a musical beat or the peak of an action? Use the
   transcript timings in `report.md` and the per-second words. A cut in the middle of a word or a
   gesture reads as a mistake. In shorts, the first frame after a cut should already be doing
   something: trim the lead-in.
3. **Eye-trace.** Where is the subject in the last frame before the cut and the first frame after?
   Same screen area: the eye stays put, and the cut is smooth. Opposite area: the eye must search for
   a moment, which spends attention. That is fine when the jump is the point, such as a shock reveal.
4. **Brightness and colour jump.** Check the `brightness jump` column. A jump of more than about 40
   levels feels like a flash. Dark-to-bright can work as a reveal. Otherwise, grade the shots to meet.
5. **Sound across the cut.** Voice or music should carry over with no pop and no gap. Check DEAD_AIR
   flags and loudness near the cut time. A J-cut (sound first) or L-cut (sound trails) smooths a hard
   picture cut.
6. **Information.** Can a muted viewer tell within about half a second what changed? If not, add a
   text pop or pick a clearer shot.
7. **Redundancy.** Do two shots in a row say the same thing? Keep the stronger one.

Log every cut in the review's transition log, including the good ones (`KEEP, on the word "wow",
match on hand position`). The log shows that every transition was checked.

## Transition taxonomy

| Transition | What it is | In a short | How it shows in the data |
|---|---|---|---|
| Hard cut | One shot replaces the next | The default. Strong when motivated. | A single-frame scene spike, scene ≥ 0.30 |
| Jump cut | Same framing, time removed | Fine in talking heads when it removes dead air. Hide it with a 110-120% punch-in on alternate cuts. | A cut whose before and after frames have the same composition |
| Punch-in / zoom cut | Same shot, tighter | Emphasis on a word. Good on the hook word. | A cut where the subject scales up |
| Cut on action | The movement starts in shot A and finishes in shot B | Hides the cut and keeps momentum | Motion continues across the cut row |
| Match cut | The shape, position or motion matches across shots | The best transition there is, and the ideal loop seam | Similar composition on both sides of the row |
| J-cut / L-cut | Audio leads or trails the picture | How the hook voice-over runs over the payoff preview | Transcript words span the cut time |
| Whip / swish / speed ramp | A fast motion blur bridges shots | Energy, but becomes noise when used everywhere | Gradual detector A (moderate scene scores across frames) |
| Dissolve / cross-fade | Two shots blend | Signals time passing, and slows a short down. Usually replace it with a hard cut. | GRADUAL_TRANSITION: steady change, one-way brightness ramp |
| Fade from black | Opens on black | At frame 0 it is a BLOCKER: the poster frame is black | FIRST_FRAME_BLACK / FIRST_FRAME_FADE_IN |
| Fade to black | Ends on black | Says "the end" and breaks the replay loop | FADE_TO_BLACK_END |
| Black mid-video | Black frames between shots | Dead time | BLACK_MID |
| Flash frame | A 1-2 frame shot | Usually a trim error. A deliberate flash on a beat can work; say which it is. | FLASH_FRAME |
| Freeze frame | The picture holds still | Only with text or sound doing the work | FROZEN_PICTURE |
| Graphic / text transition | Text or a shape wipes the frame | Good if the text carries information, decoration if not | No reliable signal; judge by eye |

## Pacing

There is no universal cuts-per-10-seconds target. A cooking reveal and a talking explainer pace
differently. Judge the **visual change cadence** instead: in a narrated short, something changes
every ~1.5-3 s (a cut, punch-in, b-roll or text pop). The report counts **visual changes**: hard
cuts plus big changes without a cut, such as animated transitions, layout changes and reveals. It
measures each frame against the frame 0.5 s earlier, so motion graphics that never hard-cut are not
mistaken for one long shot. Look at the stretches it flags (LONG_HOLD, STATIC_STRETCH) and at seconds
in `seconds.csv` with a low `change` value and no words. Each one needs a reason to exist, and "the
action is the point" is a valid reason. Text popping on is too small to register as a big change, so
read the timeline sheets for it before you call a hold dead.

Pacing should also change. A short at one constant speed is as flat as one that is uniformly slow.
Speed up through the mechanism and hold, briefly, on the payoff reaction.

## Common faults to look for

- **Pre-roll handles left in.** The first 3-10 frames after a cut are someone getting ready, with a
  blank expression or a hand moving into frame. Trim to the action.
- **Post-roll lingering.** A shot holds after the line has landed. Cut on the last syllable or one
  beat after it.
- **Accidental flash frames** left at edit points. Check every FLASH_FRAME with a `--span`.
- **A subject jumping sides** on every cut in a two-shot conversation. Keep the eye-line consistent.
- **The same shot repeated** as b-roll.
- **Transitions as decoration**, where every cut has a whoosh or glitch. One deliberate effect is
  style; ten are noise.
- **Reset joins in chained generated clips.** Each clip starts and ends on the same reference pose,
  so the host snaps back to it every few seconds, often wrapped in a pause. The join is invisible,
  but the rhythm visibly "resets" exactly where thumbs move. Fix it with TRIM AROUND: because the pose
  matches on both sides, a trim there cannot be seen.
- **The first and last frames fighting each other.** If the loop seam jumps from a dark tail to a
  bright first frame, a replay feels like a restart. If they match, it feels like more of the same
  video.
