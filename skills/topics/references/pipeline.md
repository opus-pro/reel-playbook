# The full run: from topic to polished script

Run mode chains the stages so an agent can go from "what should I make next?" to a script ready to
shoot, without asking at each step. Read for Run and Learn modes.

## Contents
1. Stages and what each one hands on
2. The project folder
3. Scoring blind
4. Hand-off to Hooks
5. Loops and stop rules
6. The final package
7. Learn: closing the loop

---

## 1. Stages and what each one hands on

| # | Stage | Done by | Hands on |
|---|---|---|---|
| 0 | Intake | this skill | `channel.md`: profile, pillars, ledger |
| 1 | Scout | this skill, `research.md` | `01-topic-board.md` |
| 2 | Concepts | this skill, `angles.md` | `02-concepts.md`: 2-3 concept cards per top topic |
| 3 | Gate | this skill's Score mode, blind | `03-gate.md`: scores, profile, verdict per card |
| 4 | Script | Hooks, Create mode | `04-brief.md`: hooks, beat sheet, script, first frame, shot plan |
| 3b | Script check | this skill's Score mode | `05-script-check.md`: PASS or FIX |
| 5 | Polish | Hooks paper review | the brief's paper-review section, with fixes applied |
| 6 | Final | this skill | `06-final.md` |
| 7 | Learn (after posting) | this skill | results appended to the ledger in `channel.md` |

**Intake asks once, then the run goes on its own.** Ask only for what is missing: the channel (URL
or a description), platform (Shorts, Reels or both), language, target length, what can actually be
filmed or generated, how many finished scripts are wanted (default 1), and whether the user wants a
checkpoint after the gate (default: no). With a channel URL, run `scout.py channel` to build the
ledger instead of asking what has been made.

## 2. The project folder

```
<channel-slug>/
  channel.md                       profile, pillars, ledger (assets/channel.md)
  <YYYY-MM-DD>-<topic-slug>/
    01-topic-board.md
    02-concepts.md
    03-gate.md
    04-brief.md                    written by Hooks
    05-script-check.md
    06-final.md
    log.md                         every loop, every verdict, and why
    research/                      scout.py --out files
```

Reuse an existing `<channel-slug>/` folder when the user has one: its ledger is how the run avoids
repeats and learns from past results.

## 3. Scoring blind

The agent that researched and wrote a concept is invested in it and will score it high. When the
Agent tool is available, run the gate in a fresh subagent:

- Give it the path to this skill's `references/entertainment-rubric.md`, the concept cards (with
  their evidence), and the channel profile. Nothing else: not the research excitement, not your
  ranking, not which card you prefer.
- Ask for the report in `assets/score-report.md` format, one per card, plus a ranking.
- Do the same for the script check, giving it the greenlit card, its gate scores and the script.

Without subagents, score each card in a separate pass, write the evidence before the number, and
say in `log.md` that the scoring was not blind.

## 4. Hand-off to Hooks

Hooks is a separate skill (`hooks`). It writes the hooks, the story and the
script, and reviews them frame by frame on paper. It does not judge whether the topic is worth
making; this skill already did.

**If Hooks is installed,** invoke it in Create mode with:

- the greenlit concept card, its gate report, and the channel profile;
- a note that the angle is already chosen and scored, so Create should treat it as its chosen story
  wrapper and start at hooks;
- the aha line, the share line and the bigger question, to keep through the script;
- platform, length, language, and what can be produced.

Ask for the brief to be saved as `04-brief.md` in the project folder. After the script check, give
any FIX notes back to Hooks as edits, and let it run its paper review on the final script.

**If Hooks is not installed,** stop after the gate. Deliver the greenlit concept with a plain
beat outline (setup, the turn where the surprise lands, the payoff, the bigger question), and say
that hooks, the script and the frame-by-frame review need Hooks.

## 5. Loops and stop rules

| Situation | Do |
|---|---|
| A card gets REWORK | Re-angle it (`angles.md`, section 4) and re-score blind. At most two rounds per card, then KILL. |
| A card gets KILL | Drop it. Note why in `log.md` so the next Scout round avoids the same trap. |
| Every card in a round is killed or exhausted | Back to Scout with what failed (for example "all like traps: look for absurd-but-true and hidden-why topics"). |
| Three Scout rounds without a GREENLIGHT | Stop. Report the best three near-misses, each with its scores and what held it back. **Never lower the bar to finish.** |
| Script check returns FIX | Send the fixes to Hooks, re-check. At most two rounds; then deliver with the open issues listed. |
| A claim can't be verified | It can't carry the concept. Re-angle around a checkable claim, or KILL. |
| More than one card greenlit | Rank by total, then by Share motive; script the top one (or as many as the user asked for). Keep the others in the ledger as a backlog. |

## 6. The final package

`06-final.md`, from `assets/final-package.md`:

- The concept card and its entertainment score (total, Aha, Share, More, profile).
- the Hooks skill's paper-review score and its verdict, side by side, never added together.
- The script, the first-frame spec and the shot plan (from the brief).
- The aha line, the share line and the bigger question, quoted from the script.
- What still needs checking (claims, permissions, what can be filmed).
- What to measure after posting, and when.

Lead the chat reply with the concept in one sentence, both scores and the top risk.

## 7. Learn: closing the loop

The pipeline improves only if results come back. After the short is posted (about 7 days later is a
fair first read):

1. Get the numbers. For YouTube, `scout.py channel` gives views; ask the user for subscribers gained
   and viewed vs swiped from YouTube Studio. For Instagram, ask for reach, plays, sends (shares), saves
   and follows from Insights.
2. Append a row to the ledger in `channel.md`: date, topic, profile, entertainment score and its
   three outcome scores, the Hooks skill's score, views ÷ subs, sends per 1,000 reach (Reels), subscribers
   or follows per 1,000 views, and one line on what you think happened.
3. Before the next Scout round, read the ledger. Topics and profiles that beat the channel's median
   are signals to serve again with new angles; scores that predicted badly are calibration notes for
   the user.

Keep the ledger in the user's project folder. Never copy results into this skill's files: the skill
is read by scorers, and a score that has seen the answers is no longer blind.
