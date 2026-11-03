---
name: hooks
description: Critically review short vertical videos (YouTube Shorts, TikTok, Reels) frame by frame - the first frame, the first 3 seconds, every cut and transition, pacing, script readability, the ending and the replay loop - and design new shorts hook first, then story. Pairs a measured ffmpeg analyzer with a strict rubric built on Jenny Hoyos's short-form method (story over topic, first-frame design, 10-year-old language, retention and loop endings) and a hook bank with rehooks for the middle. Use whenever someone asks to review, critique, roast, score, QC or improve a short, reel or TikTok, asks why a short flopped or got swiped away, wants hooks, rehooks, a first frame or a script for a short, wants to turn a topic into a short-form story, or shares Shorts analytics such as viewed vs swiped away or a retention graph - even if they never say "hook".
---

# Hooks

A short is judged by a stranger with a thumb, in under a second, often with the sound off. Hooks
reviews a video the way that stranger experiences it, one frame at a time, and then says exactly what
to change. When making a new short, it works in the same order the viewer does: the hook first, then
the story that pays the hook off.

## Pick the mode

| The user brings | Mode | You deliver |
|---|---|---|
| A video file (or a link they have downloaded) | **Review** | A critique report with a score, a cut-by-cut log, rewrites and a re-edit list |
| A topic, idea, product or rough script | **Create** | A hook-story brief: hooks, story, beat sheet, first-frame spec, script, shot plan |
| A posted short plus analytics (viewed vs swiped away, retention graph) | **Diagnose** | Where viewers left, the frame that made them leave, and the fix |

A script with no video gets Create mode steps 4-6 (script, first frame, paper review). A video
and a script together get Review mode, with the script used as the transcript.

## The stance: critical, specific, useful

The user asked for a critic, not a cheerleader. Holding that stance well means:

- **Start from "swipe".** The viewer owes the video nothing. Every frame has to earn the next one.
  Judge what a stranger experiences, never the effort or the production budget.
- **Evidence or it didn't happen.** Every finding cites a timestamp and frame, `[00:01.20 f29]`, or a
  measured value from the report. If you cannot point to it, do not claim it.
- **Every problem comes with a fix.** "The hook is weak" is noise. "Cut 0:00.0-0:00.6 and open on the
  burger at 0:27.3 with '$1' over it" is a review. Give the edit, the line or the shot.
- **Rank by impact.** One BLOCKER in the first second matters more than twenty polish notes later.
  The first frame and the first three seconds decide whether anything else is seen at all.
- **No invented numbers.** Do not predict views, retention percentages or "virality". Say which
  metric a fix should move (viewed vs swiped, retention at a timestamp, replays) and stop there.
- **Say what you could not check.** You cannot hear audio; you work from the transcript and the
  loudness data. Say so when a judgment depends on sound.
- **Rules are tools, not laws.** Jenny Hoyos's numbers (33-34 seconds, 95% completion) are one
  creator's observations. If a video breaks a rule on purpose and it works, say why it works.
- **Name what works, briefly.** List what to keep so the re-edit does not break it. Two or three
  lines, with evidence, after the problems.

Calibration: a 7/10 means "better than most shorts in the feed", not "fine". First cuts usually score
4-6 on first frame and hook. If you are scoring 8+ everywhere, go back to the anchors in
`references/review-rubric.md`. Totals repeat within about ±2 points between blind reviews, so call a
total within 2 points of the channel's bar borderline rather than pass or fail.

## Review mode

### 1. Measure

```bash
python <skill-dir>/scripts/analyze.py VIDEO --out REVIEW_DIR [--transcript captions.srt]
```

- `--transcript` takes `.srt`, `.vtt`, `.txt`, or JSON with whisper-style `segments` or `words`.
  Without one, the analyzer uses an embedded subtitle stream if the file has one. Otherwise ask the
  user for captions or the script. Failing that, `--whisper-model ggml-*.bin` (ffmpeg 8+ whisper
  filter) or `--asr faster-whisper` transcribe locally. Ask before using these, because they can
  download large models. With no transcript at all, review the picture and say the language checks
  were skipped.
- `--script script.txt` gives the punctuated script. ASR output and word timings often have no
  punctuation, so sentences get guessed from pauses and the hook-line and reading-level numbers are
  rough (the report then shows TRANSCRIPT_UNPUNCTUATED). With `--script`, sentences come from the
  script, which is trimmed to what is spoken, and timing still comes from the transcript.
- `--transcript-offset 42.5` handles a short cut from the middle of a longer recording. Check the
  "alignment check" line in the report: if few silences fall between words, the timing is off.
- `--edits 8.7,16.0` adds known edit points (clip joins, cuts from an EDL) to the cut log when they
  are too smooth to detect.
- `--span 12.0-14.5` adds a sheet with every frame in that window (end exclusive). Use it wherever
  something looks wrong: a cut that feels off, the first second, the last second. Add `--spans-only`
  to add span sheets to the same `--out` folder without re-measuring.
- Needs ffmpeg/ffprobe 6+ and Python 3.9+. Nothing else.

**Get the channel context.** Ask for (or note) the channel's subscriber count, whether it is new or
established, and whether its audience knows the face on screen. It decides two things: whether a face
in frame 1 counts as a draw or a stranger's face, and the verdict bar (80 for a new channel, 70 for an
established one; see `references/review-rubric.md`). Without it, treat faces as strangers' and use
the 80 bar, and say so.

**Look upstream when there is a project folder.** If the video comes from a production folder
(scripts, prompts, TTS or voice settings, clip lists, unused takes, a long-form recording), skim it.
Root causes often live there: dead air from a voice prompt that asks for "long pauses", a missing
first-frame text because a prompt said "no text overlays", a broken promise because the short is the
opening of a long video. Fixes that reuse material already recorded are cheaper than reshoots, so
note where that material is.

The analyzer decodes every frame and records scene change, brightness, motion and picture area in
`frames.csv`, and audio loudness and silence. It finds cuts, flash frames, dissolves and fades,
frozen, black and letterboxed stretches, long and static shots, late starts, dead air, dead tails,
language problems, and spoken turns that may be rehooks. It lays out the frames worth looking at as labelled contact sheets. "Every
frame" means every frame is measured, and every frame is viewed at the density the moment needs.
That is 10 frames per second in the hook and tail, every cut, every frame in a `--span`, and 2 per
second elsewhere.

### 2. Cold read the first frame, before opening the report

Open `frames/first_frame.png` before you read `report.md` or the transcript, as a muted stranger
would. Passing the transcript's path to the analyzer is fine; just don't read the contents yet. Write
one sentence: *"A muted stranger sees ___ and stays because ___"* (or *"swipes because ___"*). Then
check `first_frame_small.png` (still readable at feed/shelf size?), `first_frame_squint.png` (does one
shape dominate?) and `first_frame_safezones.png` (is text or the subject under the app UI?). The cold
read only works before you know the story. If you already knew it (the user told you), say so next
to the sentence.

### 3. Read `report.md`

Flags are candidates, not findings. Hold each one until you have seen it on a sheet. Read the INFO
flags first: TRANSCRIPT_UNPUNCTUATED, TRANSCRIPT_CLIPPED, TRANSCRIPT_MISALIGNED and DECODE_MISMATCH
tell you which numbers to distrust.

### 4. Walk the video in viewing order

Use the Read tool on each sheet in the order `report.md` lists them. For each:

- **Hook sheet (0-3 s, 10 fps).** First muted: what does a viewer understand by 3 s from the
  picture and on-screen text alone? Then with the transcript: is the hook said within about 2 s? Does
  the picture show a preview of the payoff while the voice states the hook? Is there visible change?
- **Story spine.** Fill in who, wants, because (stakes), constraint, mechanism, payoff, and whether
  the promise is kept (template in `assets/review-template.md`). Any slot the video does not fill is
  a finding. A topic with no stakes is the most common reason a well-made short goes nowhere.
- **Cut sheets.** One row per edit point: two frames before, two after. Edit points are hard cuts,
  *jumps* (one-frame jolts such as jump cuts, hidden joins between generated clips, or elements
  snapping on) and any `--edits` you passed. Give every edit point a verdict using the checklist in
  `references/transitions.md`: is there a reason, does it land on a word or action, is the eye-trace
  kept, is there a brightness jump? Every edit point gets a row in the transition log, even the ones
  that are fine. If the report finds none, say so in the log, check the project for clip lengths or
  an edit list, and rerun with `--edits` if joins exist. A single unbroken shot is itself a pacing
  finding.
- **Timeline sheets.** The middle: is there a mechanism, or could a viewer skip to the end and miss
  nothing? Where are the dead stretches? Cross-check `seconds.csv` for seconds with no cut, little
  motion and no words.
- **Rehook map.** A rehook closes one beat's question and opens the next, at every seam after the
  hook. Start from the report's "Rehook candidates" (spoken turns with times), confirm which ones
  actually open a question, and add the shown ones (a counter, a new obstacle) from the timeline
  sheets. Any seam with nothing opening, a rehook the video never pays off, a generic tease, or a
  signpost posing as a rehook is a finding. So is any stretch past the limit (about 10 s in a short)
  with nothing said or shown. Rehook types, faults and verdicts are in
  `references/hooks-and-rehooks.md`.
- **Tail and loop seam.** Does it end abruptly on the payoff, or drift, sign off or fade? Does the
  last frame flow back into the first?

When a moment needs closer inspection, rerun with `--span START-END --spans-only` into the same folder
and look at every frame.

Two common cases have their own notes. A short cut from a long video often keeps the long video's
signposts and ends before the payoff; see "Cutting a short from a long video" in the playbook. A
short hosted by an AI avatar has its own first-frame and artifact checks; see "AI hosts" in
`references/method.md`.

### 5. Score and write

Score the nine dimensions in `references/review-rubric.md`. That file has the weights, the anchors,
the severity definitions and the verdict rules. Confirm or dismiss every auto-flag, and list the
dismissed ones with a reason. Write the report with `assets/review-template.md`. Write it in the
user's language, and keep quoted script lines in the video's language.

Deliver the report as a markdown file next to the review folder. Include the key images inline when
the medium allows. Lead the chat reply with the verdict, the score and the top three fixes.

### 6. Re-check

After the user re-edits, run the analyzer again into a new folder. Compare flags and the hook
sheets, and confirm each fix landed without breaking anything listed under Keep.

## Create mode: hooks first, then story

Read `references/hook-story-playbook.md` first. It has the wrappers, hook patterns, scoring, the beat
sheet, the mechanism menu and ending recipes. The order matters, because each step constrains the
next:

1. **Intake.** Ask only for what is missing: topic, audience, platform, language, what can actually
   be filmed or generated, and the target length.
2. **Find the story.** Turn the topic into at least 6 story wrappers (stakes, constraint, doubter,
   test, zoom-out, transformation, mystery). A topic is not a story until someone wants something for
   a reason.
3. **Write hooks before anything else.** For the best 2-3 wrappers, write at least 10 hook packages,
   drawn from at least four hook families in `references/hooks-and-rehooks.md`. Each package has a
   spoken line (about 2 s), a first-frame spec, on-screen text and the payoff moment to preview at
   1-2.5 s. Score them with the hook rubric, kill any hook whose payoff you cannot deliver, and pick
   one. Run the hook tests on the winner, starting with the first-second cut test.
4. **Build the story backwards from the hook's promise.** Payoff first (the last 2 s), then the
   mechanism that makes the middle worth watching, then the setup. Lay it out on the beat sheet, with
   a rehook at every seam: each beat answers its own question and opens the next.
5. **Script at a 10-year-old's level.** Check it with
   `python <skill-dir>/scripts/readability.py script.txt --target 33.5`, which also lists the
   spoken turns and flags long stretches with no rehook. Cut lines, not pace.
6. **First frame and shot plan.** Draw the first frame as a spec (subject, context cue, text, safe
   zones), then the shot list with planned transitions and the loop seam.
7. **Paper review.** Run the review rubric on the brief itself. Anything under 7 on first frame or
   hook goes back to step 3.

Deliver with `assets/hook-story-brief.md`. Once a cut exists, run Review mode on it.

## Diagnose mode

Ask for the numbers the platform shows: viewed vs swiped away, average percentage viewed, and the
retention graph (a screenshot is fine). Also ask for views and the channel's subscriber count:
views ÷ subscribers is the fair way to compare Shorts across channels, since raw views mostly
measure channel size. Map each symptom to a moment with the table in
`references/review-rubric.md` (Diagnose section). Then run Review mode on the video, focused on
those timestamps, with `--span` around every drop. YouTube lets creators trim a published Short in
Studio. A cliff in the last second is the cheapest fix there is, so check for it first.

## References: when to read what

- `references/method.md`: the principles, with where they come from and how sure to be of each.
  Read once per session, before the first review or brief.
- `references/review-rubric.md`: scoring, severities, verdicts and the Diagnose table. Read for
  every review.
- `references/transitions.md`: how to judge each cut, plus the transition taxonomy. Read before
  the cut pass.
- `references/hook-story-playbook.md`: Create mode in full. Read for Create, and for the Rewrites
  section of a review.
- `references/hooks-and-rehooks.md`: 14 hook families with example lines, the four
  channels of a hook, hook tests, before-and-after rewrites, and rehooks (timing, types, rules,
  faults, the rehook map, a worked example). Read for Create steps 3-4, for the rehook map in a
  review, and for the Rewrites section.
- `assets/review-template.md` and `assets/hook-story-brief.md`: output skeletons.
