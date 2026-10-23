"""Dibuja el ovalo y los rasgos protegidos de cada cara sobre el revelado, para verificarlos.

Uso: .venv/bin/python tools/check_faces.py <foto> [...]   -> proceso/01-caras/<foto>-<cara>.png
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from common import PROCESS, linear_to_srgb, load_linear, luminance, to_uint8  # noqa: E402
from faces import window  # noqa: E402
from photos import PHOTOS  # noqa: E402


def ellipse(d: ImageDraw.ImageDraw, e, origin, color, grow=1.0) -> None:
    oy, ox = origin
    cx, cy, rx, ry = e[:4]
    ang = e[4] if len(e) > 4 else 0
    t = np.linspace(0, 2 * np.pi, 90)
    c, s = np.cos(np.radians(ang)), np.sin(np.radians(ang))
    x = rx * grow * np.cos(t)
    y = ry * grow * np.sin(t)
    pts = [(cx - ox + c * xx - s * yy, cy - oy + s * xx + c * yy) for xx, yy in zip(x, y)]
    d.line(pts + [pts[0]], fill=color, width=2)


def main(name: str) -> None:
    img = load_linear(name, "base")
    gain = 0.85 / np.percentile(luminance(img[::8, ::8]), 99)
    out = PROCESS / "01-caras"
    out.mkdir(parents=True, exist_ok=True)
    for face in PHOTOS[name]["faces"]:
        sy, sx = window(face, img.shape[:2])
        im = Image.fromarray(to_uint8(linear_to_srgb(img[sy, sx] * gain), dither=False))
        d = ImageDraw.Draw(im, "RGBA")
        # grilla cada 25 px, rotulada cada 100, en coordenadas de la foto completa
        from PIL import ImageFont

        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        for x in range((sx.start // 25 + 1) * 25, sx.stop, 25):
            d.line([(x - sx.start, 0), (x - sx.start, im.height)], fill=(255, 255, 255, 70 if x % 100 == 0 else 28))
            if x % 100 == 0:
                d.text((x - sx.start + 2, 2), str(x), fill=(255, 255, 0, 255), font=font)
        for y in range((sy.start // 25 + 1) * 25, sy.stop, 25):
            d.line([(0, y - sy.start), (im.width, y - sy.start)], fill=(255, 255, 255, 70 if y % 100 == 0 else 28))
            if y % 100 == 0:
                d.text((2, y - sy.start + 2), str(y), fill=(255, 255, 0, 255), font=font)
        ellipse(d, face["oval"], (sy.start, sx.start), (255, 210, 0))
        for e in face["features"]:
            ellipse(d, e, (sy.start, sx.start), (0, 220, 255), grow=1.15)
        im.save(out / f"{name}-{face['id']}.png")
        print(out / f"{name}-{face['id']}.png", im.size)


if __name__ == "__main__":
    for n in sys.argv[1:]:
        main(n)
