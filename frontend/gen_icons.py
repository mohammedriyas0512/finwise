"""Generate PWA PNG icons from the FinWise brand (blue rounded square + check + rupee)."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

OUT = Path(r"C:/Users/Asus/FinWise/frontend/public")
OUT.mkdir(parents=True, exist_ok=True)

BLUE = (37, 99, 235)
GREEN = (22, 163, 74)
WHITE = (255, 255, 255)


def rounded(size, radius_ratio, pad_ratio=0.0):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = int(size * pad_ratio)
    r = int(size * radius_ratio)
    d.rounded_rectangle([pad, pad, size - pad, size - pad], radius=r, fill=BLUE)
    # check mark
    s = size
    pts = [(0.28*s, 0.60*s), (0.44*s, 0.46*s), (0.56*s, 0.55*s), (0.74*s, 0.34*s)]
    d.line(pts, fill=WHITE, width=max(2, int(s*0.06)), joint="curve")
    d.ellipse([0.70*s, 0.30*s, 0.78*s, 0.38*s], fill=GREEN)
    # rupee glyph
    try:
        font = ImageFont.truetype("seguisym.ttf", int(s*0.22))
    except Exception:
        font = ImageFont.load_default()
    d.text((0.30*s, 0.66*s), "\u20b9", font=font, fill=WHITE)
    return img


for name, size, pad in [("pwa-192.png", 192, 0.0),
                        ("pwa-512.png", 512, 0.0),
                        ("pwa-maskable-512.png", 512, 0.10),
                        ("apple-touch-icon.png", 180, 0.0)]:
    rounded(size, 0.22, pad).save(OUT / name)
    print("wrote", name)
