"""Antes y despues lado a lado desde las salidas finales (editadas/), entero o un recorte.

Uso: .venv/bin/python tools/side.py <foto> salida.png [x0 y0 x1 y1] [--width 1800]
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from common import EDITED, PROCESS  # noqa: E402

Image.MAX_IMAGE_PIXELS = None


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("out")
    p.add_argument("box", nargs="*", type=int)
    p.add_argument("--width", type=int, default=1800)
    a = p.parse_args()
    ims = [Image.open(EDITED / f"{a.name}-antes.png"), Image.open(EDITED / f"{a.name}.png")]
    if a.box:
        ims = [im.crop(tuple(a.box)) for im in ims]
    w = (a.width - 6) // 2
    ims = [im.convert("RGB").resize((w, round(im.height * w / im.width)), Image.LANCZOS) for im in ims]
    out = Image.new("RGB", (2 * w + 6, ims[0].height), (20, 20, 20))
    out.paste(ims[0], (0, 0))
    out.paste(ims[1], (w + 6, 0))
    d = ImageDraw.Draw(out)
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
    d.text((8, 6), "RAW tal cual", fill=(255, 40, 160), font=font)
    d.text((w + 14, 6), "Editada", fill=(255, 40, 160), font=font)
    path = PROCESS / "40-color" / a.out
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    print(path, out.size)


if __name__ == "__main__":
    main()
