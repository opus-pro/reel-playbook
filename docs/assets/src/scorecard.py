"""Build scorecard.html from the weights in the two rubrics."""
HOOKS = [("First frame", 20), ("Hook, first 3 s", 20), ("Story and promise", 15), ("Mechanism and middle", 10), ("Pacing and transitions", 10), ("Language and readability", 10), ("Ending and loop", 10), ("Sound", 3), ("Technical and platform fit", 2)]
TOPICS = [("Share motive", 20), ("Who cares", 15), ("Surprise", 15), ("Fresh", 10), ("Click", 10), ("Arousal", 10), ("Depth", 10), ("Series and ownership", 10)]
UNIT = 11.5

def rows(items, color, strong=()):
    out = []
    for name, value in items:
        fill = color if not strong or name in strong else "#B9B3C9"
        out.append(f'<div class="row"><div class="lab">{name}</div><div class="bar" style="width:{value * UNIT}px;background:{fill}"></div><div class="val">{value}</div></div>')
    return "".join(out)

html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><link rel="stylesheet" href="base.css"><style>
body {{ height:850px; background:var(--cream2); padding:50px 60px; }}
.panels {{ display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:36px; margin-top:34px; }}
.p {{ padding:26px 30px; height:600px; }}
.p h3 {{ font-family:'Lilita One',sans-serif; font-weight:400; font-size:48px; line-height:1; }}
.note {{ font-size:26px; white-space:nowrap; font-weight:500; color:var(--muted); margin:8px 0 22px; line-height:1.15; }}
.row {{ display:grid; grid-template-columns:326px 240px 1fr; align-items:center; column-gap:12px; height:44px; }}
.lab {{ font-size:26px; font-weight:500; white-space:nowrap; }}
.bar {{ height:24px; border-radius:0 6px 6px 0; justify-self:start; }}
.val {{ font-size:27px; font-weight:700; }}
</style></head><body>
<div class="title">What gets graded, out of 100</div>
<div class="panels">
<div class="card p"><h3>Hooks: the telling</h3><div class="note">40 of 100 points are decided in the first 3 seconds.</div>{rows(HOOKS, "#FF5B4A", ("First frame", "Hook, first 3 s"))}</div>
<div class="card p"><h3>Topics: the idea</h3><div class="note">Share motive weighs most: a like is not a share.</div>{rows(TOPICS, "#7A4DFF", ("Share motive",))}</div>
</div></body></html>"""
open("scorecard.html", "w").write(html)
