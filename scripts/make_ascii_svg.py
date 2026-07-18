"""
make_ascii_svg.py
Downsample the prepped photo to a character grid, map brightness to a
density ramp, and emit a self-typing monochrome SVG (row-by-row wipe).

Usage:
    python scripts/make_ascii_svg.py
Reads:
    scripts/prepped-photo.png
Writes:
    avi-ascii.svg   (rename the constants below to your own file)
"""
from PIL import Image

INPUT_IMAGE = "scripts/prepped-photo.png"
OUTPUT_SVG = "avi-ascii.svg"

COLS = 100
ROWS = 53
CHAR_W = 7.2   # px per character cell, monospace-ish
CHAR_H = 12
FONT_SIZE = 12
FILL_COLOR = "#c9d1d9"   # light gray, monochrome only
BG_COLOR = "#0d1117"

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense)


def brightness_to_char(v: int) -> str:
    # v is 0-255, invert so dark pixels -> dense chars
    idx = int((v / 255) * (len(RAMP) - 1))
    return RAMP[len(RAMP) - 1 - idx]


def build_grid(path: str):
    img = Image.open(path).convert("L").resize((COLS, ROWS))
    px = img.load()
    rows = []
    for y in range(ROWS):
        row_chars = []
        for x in range(COLS):
            row_chars.append(brightness_to_char(px[x, y]))
        rows.append("".join(row_chars))
    return rows


def escape(c: str) -> str:
    return {"<": "&lt;", ">": "&gt;", "&": "&amp;"}.get(c, c)


def render_svg(rows):
    width = COLS * CHAR_W
    height = ROWS * CHAR_H
    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, monospace" font-size="{FONT_SIZE}">'
    )
    parts.append(f'<rect width="{width}" height="{height}" fill="{BG_COLOR}"/>')

    stagger = 0.035  # seconds between row starts
    row_dur = 0.5    # seconds for a row's wipe to complete

    for i, row_text in enumerate(rows):
        y = (i + 1) * CHAR_H - 2
        start = i * stagger
        clip_id = f"clip{i}"
        text_escaped = "".join(escape(c) for c in row_text)

        # Clip rect that animates its width from 0 -> full row width
        parts.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="0" y="{y - CHAR_H + 2}" width="0" height="{CHAR_H}">'
            f'<animate attributeName="width" from="0" to="{width}" '
            f'begin="{start:.3f}s" dur="{row_dur}s" fill="freeze" '
            f'calcMode="linear"/>'
            f'</rect>'
            f'</clipPath>'
        )
        parts.append(
            f'<text x="0" y="{y}" fill="{FILL_COLOR}" clip-path="url(#{clip_id})" '
            f'xml:space="preserve">{text_escaped}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    grid = build_grid(INPUT_IMAGE)
    svg = render_svg(grid)
    with open(OUTPUT_SVG, "w") as f:
        f.write(svg)
    print(f"Wrote {OUTPUT_SVG}")
