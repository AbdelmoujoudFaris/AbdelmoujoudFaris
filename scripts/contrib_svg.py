"""Draw GitHub's own contribution calendar as contrib.svg (refreshed by a GitHub Action)."""
import datetime as dt
import re
import urllib.request
from pathlib import Path

USER = "AbdelmoujoudFaris"
html = urllib.request.urlopen(f"https://github.com/users/{USER}/contributions", timeout=30).read().decode("utf-8")
total = re.search(r"([\d,]+)\s+contributions?\s+in the last year", html).group(1)
tips = {m.group(1): m.group(2).strip() for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', html)}
days = []
for m in re.finditer(r'<td[^>]*data-date="([\d-]+)"[^>]*>', html):
    td = m.group(0)
    cid = re.search(r'id="([^"]+)"', td)
    lvl = re.search(r'data-level="(\d)"', td)
    days.append((m.group(1), int(lvl.group(1)) if lvl else 0, tips.get(cid.group(1), "") if cid else ""))
days.sort()

COLORS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
CELL, GAP, LEFT, TOP = 10, 3, 36, 46
first = dt.date.fromisoformat(days[0][0])
pad = (first.weekday() + 1) % 7                     # weeks start on Sunday
weeks = (pad + len(days) + 6) // 7
W, H = LEFT + weeks * (CELL + GAP) + 16, TOP + 7 * (CELL + GAP) + 34
font = 'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"'
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" {font}>',
     f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="6" fill="#fff" stroke="#d0d7de"/>',
     f'<text x="16" y="24" font-size="15" fill="#1f2328">{total} contributions in the last year</text>']
last_m = None
for w in range(weeks):
    i = max(w * 7 - pad, 0)
    if i < len(days):
        d = dt.date.fromisoformat(days[i][0])
        if d.month != last_m and w < weeks - 2:
            o.append(f'<text x="{LEFT + w * (CELL + GAP)}" y="{TOP - 6}" font-size="10" fill="#1f2328">{d:%b}</text>')
        last_m = d.month
for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    o.append(f'<text x="8" y="{TOP + r * (CELL + GAP) + 9}" font-size="10" fill="#1f2328">{name}</text>')
for k, (date, lvl, tip) in enumerate(days):
    pos = pad + k
    x, y = LEFT + (pos // 7) * (CELL + GAP), TOP + (pos % 7) * (CELL + GAP)
    o.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{COLORS[lvl]}" '
             f'stroke="rgba(27,31,36,0.06)"><title>{tip or date}</title></rect>')
ly = H - 14
o.append(f'<text x="16" y="{ly + 9}" font-size="10" fill="#59636e">Learn how we count contributions</text>')
lx = W - 16 - 5 * (CELL + 3) - 28
o.append(f'<text x="{lx - 28}" y="{ly + 9}" font-size="10" fill="#59636e">Less</text>')
for k, c in enumerate(COLORS):
    o.append(f'<rect x="{lx + k * (CELL + 3)}" y="{ly}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
o.append(f'<text x="{lx + 5 * (CELL + 3) + 4}" y="{ly + 9}" font-size="10" fill="#59636e">More</text>')
o.append("</svg>")
Path(__file__).resolve().parent.parent.joinpath("contrib.svg").write_text("\n".join(o), encoding="utf-8")
print(f"{total} contributions, {len(days)} days")
