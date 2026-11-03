"""Build proof.html from docs/hooks-calibration.md: (grade, views / subscribers, round)."""
import math

DATA = [
    (78, 8.6, 1), (74, 14.9, 1), (70, 2.7, 1), (68, 0.34, 1), (68, 0.004, 1), (60, 1.3, 1), (56, 7.2, 1), (48, 0.48, 1),
    (76, 2.9, 2), (73, 13.8, 2), (71.8, 1.2, 2), (65, 0.01, 2), (62.7, 32, 2), (61.7, 0.095, 2),
]
# Where each value label sits relative to its dot: (x offset, y offset, anchor).
LABELS = {
    (73, 13.8): (0, 58, "middle"),
    (71.8, 1.2): (30, 42, "start"),
    (68, 0.34): (-30, 11, "end"),
    (68, 0.004): (-30, 11, "end"),
    (65, 0.01): (-30, 11, "end"),
    (60, 1.3): (0, -32, "middle"),
}
L, R, T, B = 200, 1520, 300, 820
X0, X1, Y0, Y1 = 40, 85, 0.002, 60
HIGH, LOW = "#FF5B4A", "#7A4DFF"
HIGH_PALE, LOW_PALE = "#FFC9C2", "#D3C4FF"


def x(g):
    return L + (g - X0) / (X1 - X0) * (R - L)


def y(v):
    return B - (math.log10(v) - math.log10(Y0)) / (math.log10(Y1) - math.log10(Y0)) * (B - T)


parts = []
parts.append(f'<rect x="{x(70)}" y="{T}" width="{R-x(70)}" height="{B-T}" fill="#FF5B4A" fill-opacity=".09"/>')
for tick in (0.01, 0.1, 10):
    parts.append(f'<line x1="{L}" x2="{R}" y1="{y(tick)}" y2="{y(tick)}" stroke="#E2D7C2" stroke-width="2"/>')
for tick in (0.01, 0.1, 1, 10):
    parts.append(f'<text x="{L-18}" y="{y(tick)+10}" class="ax" text-anchor="end">{tick:g}×</text>')
for tick in (40, 50, 60, 70, 80):
    parts.append(f'<text x="{x(tick)}" y="{B+44}" class="ax" text-anchor="middle">{tick}</text>')
parts.append(f'<line x1="{x(70)}" x2="{x(70)}" y1="{T}" y2="{B}" stroke="#17133F" stroke-width="4" stroke-dasharray="4 12" stroke-linecap="round"/>')
parts.append(f'<text x="{x(70)+16}" y="{T-16}" class="tag">Graded 70 or higher</text>')
parts.append(f'<line x1="{L}" x2="{R}" y1="{y(1)}" y2="{y(1)}" stroke="#17133F" stroke-width="3" stroke-dasharray="14 10"/>')
parts.append(f'<text x="{L+14}" y="{y(1)-14}" class="ax2">1×: as many views as subscribers</text>')
for g, v, rnd in DATA:
    hi = g >= 70
    fill = (HIGH if hi else LOW) if rnd == 2 else (HIGH_PALE if hi else LOW_PALE)
    if hi:
        parts.append(f'<circle cx="{x(g)}" cy="{y(v)}" r="19" fill="{fill}" stroke="#17133F" stroke-width="5"/>')
    else:
        s = 17
        parts.append(f'<rect x="{x(g)-s}" y="{y(v)-s}" width="{s*2}" height="{s*2}" rx="7" fill="{fill}" stroke="#17133F" stroke-width="5"/>')
    dx, dy, anchor = LABELS.get((g, v), (30, 11, "start"))
    parts.append(f'<text x="{x(g)+dx}" y="{y(v)+dy}" class="val" text-anchor="{anchor}">{v:g}×</text>')

html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><link rel="stylesheet" href="base.css"><style>
body {{ height:1040px; background:var(--cream); padding:46px 60px; position:relative; }}
.ax {{ font:500 30px 'Fredoka',sans-serif; fill:#5B5675; }}
.ax2 {{ font:600 30px 'Fredoka',sans-serif; fill:#17133F; }}
.tag {{ font:600 32px 'Fredoka',sans-serif; fill:#17133F; }}
.val {{ font:700 32px 'Fredoka',sans-serif; fill:#17133F; }}
.yl {{ font:600 30px 'Fredoka',sans-serif; fill:#17133F; }}
svg {{ position:absolute; left:0; top:0; }}
.key {{ position:absolute; left:60px; top:216px; display:flex; gap:30px; font-size:28px; font-weight:500; color:var(--muted); align-items:center; }}
.dot {{ display:inline-block; width:26px; height:26px; border:4px solid var(--ink); border-radius:50%; vertical-align:-4px; margin-right:10px; }}
.foot {{ position:absolute; left:60px; right:60px; top:900px; font-size:30px; font-weight:500; color:var(--muted); line-height:1.22; }}
</style></head><body>
<div class="title" style="font-size:64px">14 well-known Shorts, graded blind</div>
<div class="sub" style="font-size:33px;margin-top:6px;width:1480px">Every Short graded 70 or higher got more views than its channel has subscribers. Most below 70 didn't.</div>
<svg width="1600" height="1040">{''.join(parts)}
<text transform="translate(50 {(T+B)/2}) rotate(-90)" class="yl" text-anchor="middle">Views ÷ subscribers (log scale)</text>
</svg>
<div class="key"><span><span class="dot" style="background:{HIGH}"></span><span class="dot" style="background:{LOW};border-radius:6px"></span>Newest round</span><span><span class="dot" style="background:{HIGH_PALE}"></span><span class="dot" style="background:{LOW_PALE};border-radius:6px"></span>First round, older rubric</span></div>
<div class="foot">Horizontal axis: Hooks grade out of 100. Small, uneven test: rank correlation 0.36. Its biggest miss: a Short graded 62.7 hit 32×, while one from the same channel graded 65 hit 0.01×. A pattern in these videos, not a promise for yours.</div>
</body></html>"""
open("proof.html", "w", encoding="utf-8").write(html)
