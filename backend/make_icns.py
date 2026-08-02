"""Generate a macOS .icns icon from the FinWise brand (blue rounded square).

Run on macOS (uses the built-in `iconutil`). Generates backend/finwise.icns,
which BUILD_MAC.sh / pack_mac_app.py pick up for the .app bundle.

Usage on a Mac:  python3 make_icns.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required: pip install pillow")

HERE = Path(__file__).resolve().parent
OUT = HERE / "finwise.icns"

BLUE = (37, 99, 235)
GREEN = (22, 163, 74)
WHITE = (255, 255, 255)


def rounded(size, radius_ratio, pad_ratio=0.0):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = int(size * pad_ratio)
    r = int(size * radius_ratio)
    d.rounded_rectangle([pad, pad, size - pad, size - pad], radius=r, fill=BLUE)
    s = size
    pts = [(0.28 * s, 0.60 * s), (0.44 * s, 0.46 * s),
           (0.56 * s, 0.55 * s), (0.74 * s, 0.34 * s)]
    d.line(pts, fill=WHITE, width=max(2, int(s * 0.06)), joint="curve")
    d.ellipse([0.70 * s, 0.30 * s, 0.78 * s, 0.38 * s], fill=GREEN)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
                                  int(s * 0.22))
    except Exception:
        font = ImageFont.load_default()
    d.text((0.30 * s, 0.66 * s), "\u20b9", font=font, fill=WHITE)
    return img


def main() -> int:
    if sys.platform != "darwin":
        print("This script generates a .icns and must run on macOS (needs iconutil).",
              file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        iconset = td / "finwise.iconset"
        iconset.mkdir()
        # Standard macOS icon sizes.
        for sz in (16, 32, 64, 128, 256, 512):
            im = rounded(sz * 2, 0.22) if sz >= 256 else rounded(sz, 0.22)
            if sz >= 256:
                im.save(iconset / f"icon_{sz}x{sz}.png")
                small = rounded(sz, 0.22)
                small.save(iconset / f"icon_{sz//2}x{sz//2}@2x.png")
            else:
                im.save(iconset / f"icon_{sz}x{sz}.png")
                im2 = rounded(sz, 0.22)
                im2.save(iconset / f"icon_{sz}x{sz}@2x.png")
        subprocess.run(["iconutil", "--convert", "icns",
                        "--output", str(OUT), str(iconset)], check=True)
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
