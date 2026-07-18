"""
make_info_card.py
Hand-authored neofetch-style info card. Edit the DATA dict below with
your own details, then run this script.

Usage:
    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py   # frozen frame preview
Writes:
    info-card.svg
"""
import os

OUTPUT_SVG = "info-card.svg"

# ---- EDIT THIS SECTION WITH YOUR OWN INFO ----
TITLE = "AnupojuRohit@github"
DATA = [
    ("Now", "Building things with Python + SVG"),
    ("Prev", "Backend engineer, AI Product Engineer"),
    ("Stack", "Python · NextJs · React · Postgres"),
    ("Highlights", "Open source contributor · 3x hackathon winner"),
]
# ------------------------------------------------

BG = "#0d1117"
PANEL_BG = "#161b22"
BORDER = "#30363d"
KEY_COLOR = "#39d353"
VAL_COLOR = "#c9d1d9"
TITLE_COLOR = "#58a6ff"

WIDTH = 490
LINE_H = 34
PAD_TOP = 60


def build_svg(static: bool) -> str:
    height = PAD_TOP + LINE_H * len(DATA) + 30
    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, monospace" font-size="15">'
    )
    parts.append(
        f'<rect x="1" y="1" width="{WIDTH-2}" height="{height-2}" rx="8" '
        f'fill="{PANEL_BG}" stroke="{BORDER}"/>'
    )
    # title bar
    parts.append(f'<circle cx="20" cy="20" r="6" fill="#ff5f56"/>')
    parts.append(f'<circle cx="40" cy="20" r="6" fill="#ffbd2e"/>')
    parts.append(f'<circle cx="60" cy="20" r="6" fill="#27c93f"/>')
    parts.append(
        f'<text x="20" y="45" fill="{TITLE_COLOR}" font-weight="bold">{TITLE}</text>'
    )
    parts.append(f'<line x1="20" y1="52" x2="{WIDTH-20}" y2="52" stroke="{BORDER}"/>')

    for i, (key, val) in enumerate(DATA):
        y = PAD_TOP + i * LINE_H
        group_attrs = ""
        if not static:
            delay = 0.3 + i * 0.25
            group_attrs = f' opacity="0"'
        parts.append(f'<g{group_attrs}>')
        if not static:
            parts.append(
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            )
            parts.append(
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-10 0" to="0 0" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            )
        parts.append(
            f'<text x="20" y="{y}" fill="{KEY_COLOR}" font-weight="bold">{key}:</text>'
        )
        parts.append(f'<text x="130" y="{y}" fill="{VAL_COLOR}">{val}</text>')
        parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    static = os.environ.get("STATIC") == "1"
    svg = build_svg(static)
    with open(OUTPUT_SVG, "w") as f:
        f.write(svg)
    print(f"Wrote {OUTPUT_SVG} (static={static})")
