# Topics

**Decide what's worth making before anyone writes a hook.** Topics is an agent skill for short
vertical video (YouTube Shorts, Instagram Reels, TikTok). It researches what to make next from open
sources, shapes topics into concepts with a clear angle, and scores each concept for **entertainment
value**: does a stranger get an aha, want to send it to someone, and want more? A video that is only
pleasant gets a like and stops. Topics is built to catch that before the script.

It is the companion to Hooks, a separate skill that makes the
telling as strong as the idea: hooks, rehooks, the first frame, pacing and a frame-by-frame review.
Each works alone. Together they run from topic to a polished, ready-to-shoot script.

## What it does

| You bring | Mode | You get |
|---|---|---|
| A channel, a niche, or "what should I post next?" | **Scout** | A topic board and concept cards, each with dated evidence: outliers, audience questions, trends, freshness |
| An idea, a concept, a script or a video | **Score** | A verdict (GREENLIGHT, REWORK or KILL), a total out of 100, Aha / Share / More scores, the profile (like trap, dead-end news, hit shape...) and three re-angles when it needs work |
| "Make my next short" | **Run** | The full pipeline: research, concepts, a blind gate, the script and polish through Hooks, and a final package with both scores |
| A posted short's results | **Learn** | A ledger row comparing the scores with what happened, read before the next round |

## The entertainment score

Eight dimensions about the idea, never the telling. Hook wording, the first frame and pacing are
The Hooks skill's job.

| Group | Dimension | Weight | The test |
|---|---|---|---|
| Foundation | Who cares | 15 | Name three different strangers who'd stop, and why |
| Foundation | Fresh | 10 | How many recent videos make this exact point, and did they work? |
| Aha | Surprise | 15 | "Before, viewers think ___. After, they know ___." |
| Aha | Click | 10 | Say the why in one breath to a 10-year-old. Is it true? |
| Share | Share motive | 20 | Write the message the sharer types, and who it goes to |
| Share | Arousal | 10 | Name the feeling and how strong it is |
| More | Depth | 10 | What bigger question does the payoff leave? |
| More | Series and ownership | 10 | Is there an episode 2, and could only this channel make it? |

Every dimension has anchors from 0 to 10. A concept is greenlit only when the total clears the bar
**and** the Share motive and Aha (or Arousal) floors hold, so a broad, pleasant idea can't pass on
breadth alone. Unverifiable claims cap the Click score: the skill rewards a deep topic said simply,
never an unchecked claim said confidently.

The score names the shape of the problem:

- **Like trap:** pleasant and broad, but nothing new and nothing to send.
- **Dead-end news:** watched to the end, then never followed up.
- **Trivia nobody asked for:** true and odd, but nobody has a stake in it.
- **Smart but cold:** a clever explanation that nobody feels.
- **Hit shape:** a real surprise, a reason to send it, and a door to more.

## Topic research

`skills/topics/scripts/scout.py` uses open sources only: yt-dlp for YouTube, Google Trends,
and Wikipedia.

```bash
python skills/topics/scripts/scout.py channel https://www.youtube.com/@handle
```

```bash
python skills/topics/scripts/scout.py search "dog mayor" --n 15
```

```bash
python skills/topics/scripts/scout.py comments https://www.youtube.com/shorts/VIDEO_ID
```

```bash
python skills/topics/scripts/scout.py trends --geo US,GB
```

```bash
python skills/topics/scripts/scout.py wiki --lang en
```

| Command | What it gives |
|---|---|
| `channel` | A channel's recent Shorts against its own median: what's been made, and what its audience already rewarded |
| `search` | Shorts on a topic ranked by **views ÷ subscribers** (3x or more is a breakout, with a 10,000-view floor so tiny channels don't count), plus age, views per day and reaction rates. Shows whether an angle is crowded, tried and flat, or untouched |
| `comments` | Top-level comments that ask a question or ask for more, ranked by likes |
| `trends` | Google Trends daily searches by country |
| `wiki` | Wikipedia most-read, Did You Know and In the news |

Every report is markdown; `--out DIR` also saves the raw JSON. Nothing signs in, spoofs a browser
or works around a bot check. Instagram has no open source, so Reels topics are researched through
Shorts, trends and the web, and the creator's own Insights feed the Learn step.

## Install

Topics ships in the same plugin as Hooks. From the folder that holds this `shorts-hook-skill` folder (unzipped or cloned):

```bash
claude plugin marketplace add ./shorts-hook-skill
```

```bash
claude plugin install shorts-hook-skill@shorts-hook-skill
```

**Claude Code (copy the skill):** copy `skills/topics/` into `~/.claude/skills/` for every
project, or into `.claude/skills/` for one project.

**Other agents:** `SKILL.md` is plain markdown and the script is plain Python.

### Requirements

- Python 3.9+
- For research: `pip install yt-dlp`. Full YouTube metadata needs a JavaScript runtime (node or
  deno); the script uses node automatically.
- Scoring needs nothing but the agent.

## Use it

- "What should I post next? My channel is youtube.com/@handle."
- "Is this idea worth making, or will it just get likes? A town that elects a dog as mayor."
- "Score these three concepts and tell me which one to film."
- "I wrote the script. Check it didn't lose what made the idea good."
- "Plan my next Reel end to end, research to script."

## How much to trust it

The parts rest on solid ground: curiosity as an information gap, high-arousal emotion driving
sharing, sharing as a way of presenting yourself, and Instagram's own statement that sends per reach
are a top ranking signal. The sources are in
[`references/why-people-share.md`](../skills/topics/references/why-people-share.md).

**The score itself is not calibrated yet.** The weights and the 70 bar are a reasoned starting
point, not a measured line, and the skill says so in every report. The calibration plan, and later
its results, live in [`docs/hooks-calibration.md`](topics-calibration.md): blind scoring of same-channel hit
and control pairs against views ÷ subscribers, and against TikTok's public share counts for the
Share score. The best data is your own: the Learn step records the scores before posting and the
results after.

## Limits

- **No Instagram, TikTok or Bilibili data.** These block scripted access, and Topics doesn't work
  around it.
- **YouTube hides share counts.** On YouTube, reach is read from views ÷ subscribers, not shares.
- **The score judges the idea on paper.** Timing, luck and execution still decide a lot.
- **Web search results are US-centred.**

## Development

```bash
python tests/topics/test_scout.py
```

The tests run offline on fixtures in `tests/topics/fixtures/`: the reach math and its small-channel floor,
ranking, channel outliers, comment mining, and the Trends and Wikipedia parsers. Eval cases for the
skill are in `evals/`, outside the skill folder so the agent under test can't read the graders. Run
them with:

```bash
claude plugin eval . --scaffold --allow-tools Write Edit
```

No case needs a shell. Granting Bash on Windows makes the run refuse to start, because there is no
sandbox for it there.

Calibration data (scores of named videos, view counts) stays in `docs/`, never in `skills/`: scorers
read the skill folder, and a blind test only works if the answers aren't in it.

## License

MIT. See [LICENSE](../LICENSE).
