#!/usr/bin/env python3
"""
Render data/contributions.json (produced by fetch_contributions.py) as an
area/line activity graph SVG (weekly contribution totals), replacing the
third-party github-readme-activity-graph service. The line draws itself once
on load (CSS keyframes) and then stays put.

Run by .github/workflows/update-profile-art.yml after fetch_contributions.py.
"""
import datetime
import json
import os

HERE = os.path.dirname(__file__)
IN_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "activity-graph.svg")

BG = "#0d1117"
GRID = "#21262d"
MUTED = "#7d8590"
TEXT = "#e6edf3"
LINE = "#10b981"
AREA = "#065f46"

W, H = 900, 260
LEFT, RIGHT, TOP, BOTTOM = 44, 20, 46, 34


def weekly_totals(days):
    weeks = []
    for i in range(0, len(days), 7):
        chunk = days[i:i + 7]
        weeks.append((chunk[0]["date"], sum(d["count"] for d in chunk)))
    return weeks


def main():
    with open(IN_PATH) as f:
        data = json.load(f)
    weeks = weekly_totals(data["days"])
    peak = max(v for _, v in weeks) or 1
    ymax = ((peak + 9) // 10) * 10

    pw, ph = W - LEFT - RIGHT, H - TOP - BOTTOM
    step = pw / (len(weeks) - 1)
    pts = [(LEFT + i * step, TOP + ph - (v / ymax) * ph) for i, (_, v) in enumerate(weeks)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{LEFT},{TOP + ph} {line} {pts[-1][0]:.1f},{TOP + ph}"

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="Weekly contribution activity for {data["username"]}">',
        "<defs>"
        f'<linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{AREA}" stop-opacity="0.9"/>'
        f'<stop offset="1" stop-color="{AREA}" stop-opacity="0.05"/></linearGradient></defs>',
        "<style>"
        ".l{stroke-dasharray:3000;stroke-dashoffset:3000;animation:draw 2.4s ease-out forwards}"
        "@keyframes draw{to{stroke-dashoffset:0}}"
        ".a{opacity:0;animation:fade 1.2s ease-out 1.2s forwards}"
        "@keyframes fade{to{opacity:1}}"
        "text{font-family:'Segoe UI',Ubuntu,Sans-Serif}</style>",
        f'<rect width="{W}" height="{H}" rx="6" fill="{BG}"/>',
        f'<text x="{LEFT}" y="28" font-size="16" font-weight="600" fill="{LINE}">Contribution Graph</text>',
        f'<text x="{W - RIGHT}" y="28" font-size="12" text-anchor="end" fill="{MUTED}">'
        f'{data["total_contributions"]} contributions in the last year</text>',
    ]

    for i in range(5):
        v = ymax * i // 4
        y = TOP + ph - (v / ymax) * ph
        out.append(f'<line x1="{LEFT}" x2="{W - RIGHT}" y1="{y:.1f}" y2="{y:.1f}" stroke="{GRID}"/>')
        out.append(f'<text x="{LEFT - 8}" y="{y + 4:.1f}" font-size="11" text-anchor="end" fill="{MUTED}">{v}</text>')

    last_month = None
    for i, (date, _) in enumerate(weeks):
        d = datetime.date.fromisoformat(date)
        if d.month != last_month:
            last_month = d.month
            out.append(f'<text x="{pts[i][0]:.1f}" y="{H - 12}" font-size="11" text-anchor="middle" '
                       f'fill="{MUTED}">{d.strftime("%b")}</text>')

    out.append(f'<polygon class="a" points="{area}" fill="url(#fill)"/>')
    out.append(f'<polyline class="l" points="{line}" fill="none" stroke="{LINE}" stroke-width="2" '
               'stroke-linejoin="round" stroke-linecap="round"/>')
    px, py = pts[peak and [v for _, v in weeks].index(peak)]
    out.append(f'<circle class="a" cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{LINE}"/>')
    out.append(f'<text class="a" x="{px:.1f}" y="{py - 10:.1f}" font-size="11" text-anchor="middle" '
               f'fill="{TEXT}">{peak}</text>')
    out.append("</svg>")

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(out))
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
