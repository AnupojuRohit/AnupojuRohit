"""
prep_photo.py
Turn a normal photo into a clean, high-contrast, background-removed
grayscale image that's ready for ASCII conversion.

Usage:
    python scripts/prep_photo.py source-photo.jpg
Output:
    scripts/prepped-photo.png
"""
import sys
import io
import numpy as np
import cv2
from PIL import Image
from rembg import remove


def prep(input_path: str, output_path: str = "scripts/prepped-photo.png"):
    with open(input_path, "rb") as f:
        input_bytes = f.read()

    # 1. Remove background -> RGBA with transparent bg
    result_bytes = remove(input_bytes)
    img = Image.open(io.BytesIO(result_bytes)).convert("RGBA")

    # 2. Composite onto pure white (so bg maps to blank end of ASCII ramp)
    white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, img).convert("RGB")

    # 3. Boost local contrast with CLAHE (grayscale)
    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    Image.fromarray(enhanced).save(output_path)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <source-photo.jpg>")
        sys.exit(1)
    prep(sys.argv[1])
