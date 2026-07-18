"""
render_heatmap_svg.py
Render data/contributions.json as a 53-week x 7-day grid of rounded
boxes with a diagonal slide-down reveal (CSS keyframes, plays once).

Usage:
    python scripts/render_heatmap_svg.py
Reads:
    data/contributions.json
Writes:
    contrib-heatmap.svg
"""
import json
from datetime import datetime

INPUT_JSON = "data/contributions.json"
OUTPUT_SVG = "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
# index 0 = no contributions ... index 5 = neon top end (custom "extra bright" tier)

CELL = 12
GAP = 3
LEFT_PAD = 30
TOP_PAD = 20
BOTTOM_PAD = 55


def load_data():
    with open(INPUT_JSON) as f:
        return json.load(f)


def week_columns(days):
    """Group flat day list into a list of weeks (each a list of 7 day dicts, Sun-Sat)."""
    weeks = []
    week = []
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        dow = (dt.weekday() + 1) % 7  # convert Mon=0 -> Sun=0
        if dow == 0 and week:
            weeks.append(week)
            week = []
        week.append(d)
    if week:
        weeks.append(week)
    return weeks


def color_for_level(level: int) -> str:
    return PALETTE[min(level, len(PALETTE) - 1)]


def build_svg(data: dict) -> str:
    weeks = week_columns(data["days"])
    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * (CELL + GAP)
    height = TOP_PAD + 7 * (CELL + GAP) + BOTTOM_PAD

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, monospace" font-size="12">'
    )
    parts.append(f'<rect width="{width}" height="{height}" fill="#0d1117"/>')

    parts.append("<style>")
    parts.append(
        "@keyframes revealCell { from { opacity: 0; transform: translateY(-6px); } "
        "to { opacity: 1; transform: translateY(0); } }"
    )
    parts.append(".cell { animation: revealCell 0.35s ease-out both; }")
    parts.append("</style>")

    max_delay = 0.0
    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            x = LEFT_PAD + wi * (CELL + GAP)
            y = TOP_PAD + di * (CELL + GAP)
            level = day.get("level", 0)
            fill = color_for_level(level)
            delay = (wi + di) * 0.012  # diagonal stagger
            max_delay = max(max_delay, delay)
            parts.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2.5" fill="{fill}" style="animation-delay:{delay:.3f}s" '
                f'data-date="{day["date"]}">'
                f'<title>{day["date"]}: {day["count"]} contributions</title>'
                f'</rect>'
            )

    # legend: Less -> More
    legend_y = height - BOTTOM_PAD + 25
    parts.append(f'<text x="{LEFT_PAD}" y="{legend_y}" fill="#8b949e">Less</text>')
    lx = LEFT_PAD + 40
    for c in PALETTE:
        parts.append(f'<rect x="{lx}" y="{legend_y-10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
        lx += CELL + GAP
    parts.append(f'<text x="{lx+8}" y="{legend_y}" fill="#8b949e">More</text>')

    # stats footer
    stats = data["stats"]
    footer = f'{stats["total_last_year"]} contributions in the last year'
    parts.append(
        f'<text x="{LEFT_PAD}" y="{legend_y+22}" fill="#c9d1d9" font-weight="bold">{footer}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    data = load_data()
    svg = build_svg(data)
    with open(OUTPUT_SVG, "w") as f:
        f.write(svg)
    print(f"Wrote {OUTPUT_SVG}")
