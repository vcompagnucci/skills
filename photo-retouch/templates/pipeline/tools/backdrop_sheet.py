"""Hoja de los fondos de una foto: la maestra y los tres estilos, y el borde de cada cabeza de cerca.

Arriba, las cuatro enteras. Abajo, por cara, la cabeza (pelo de arriba y de los costados) en las
cuatro, ampliada `--zoom` veces sin suavizar, para ver el contorno pixel por pixel.

Con --box=x0,y0,x1,y1 (fracciones del ancho y del alto) suma una fila con esa zona, para mirar lo que no es
pelo: la banqueta, las zapatillas, el hueco entre las piernas. Se puede repetir.

Uso: .venv/bin/python tools/backdrop_sheet.py <foto> --preview   (el piloto: work/estilos/piloto/)
     .venv/bin/python tools/backdrop_sheet.py <foto>             (las maestras de editadas/)
     .venv/bin/python tools/backdrop_sheet.py <foto> --preview --box=0.25,0.75,0.75,1 --name=abajo
Deja proceso/estilos-pared-piloto-<foto>.png o proceso/estilos-pared-<foto>.png (con --name, -<nombre> al final).
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from common import EDITED, PROCESS  # noqa: E402
from photos import PHOTOS  # noqa: E402
from styles import PREVIEW, STYLES  # noqa: E402

FONT = "/System/Library/Fonts/Helvetica.ttc"
TOP_H = 720  # alto de cada foto entera en la hoja
CROP_W = 520  # ancho de cada recorte ya ampliado


def load(path: Path) -> Image.Image:
    with Image.open(path) as im:
        return im.convert("RGB")


def main(name: str, preview: bool, zoom: int, boxes=(), tag: str = "") -> Path:
    if preview:
        files = [PREVIEW / f"{name}-maestra.png"] + [PREVIEW / f"{name}-{k}.png" for k in STYLES]
    else:
        files = [EDITED / f"{name}.png"] + [EDITED / f"{name}-{k}.png" for k in STYLES]
    labels = ["Maestra"] + [f"{s['name']} ({s['ref']})" for s in STYLES.values()]
    imgs = [load(f) for f in files]
    w0, h0 = imgs[0].size
    native_h = 6246 if h0 > w0 else 4170
    scale = h0 / native_h
    font = ImageFont.truetype(FONT, 20, index=1)
    small = ImageFont.truetype(FONT, 16)
    tw = round(w0 * TOP_H / h0)
    side = (CROP_W // zoom) // 2 * 2
    heads = []
    for f in PHOTOS[name]["faces"]:
        cx, cy, rx, ry = (v * scale for v in f["oval"][:4])
        # la cabeza: de un poco arriba del pelo a la mitad de la cara, y los dos costados
        x0 = int(np.clip(cx - side / 2, 0, w0 - side))
        y0 = int(np.clip(cy - 1.45 * ry - side * 0.25, 0, h0 - side))
        heads.append((f.get("id", "cara"), (x0, y0, x0 + side, y0 + side)))
    for fx0, fy0, fx1, fy1 in boxes:
        bw, bh = round((fx1 - fx0) * w0), round((fy1 - fy0) * h0)
        heads.append((f"zona {fx0:g},{fy0:g},{fx1:g},{fy1:g}", (round(fx0 * w0), round(fy0 * h0), round(fx0 * w0) + max(bw, bh), round(fy0 * h0) + max(bw, bh))))
    col, ccol = tw + 20, CROP_W + 20
    width = 20 + 4 * max(col, ccol)
    height = 60 + TOP_H + 30 + len(heads) * (CROP_W + 50)
    canvas = Image.new("RGB", (width, height), (24, 24, 26))
    d = ImageDraw.Draw(canvas)
    for i, (im, lab) in enumerate(zip(imgs, labels)):
        x = 20 + i * col
        d.text((x, 18), lab, fill=(240, 240, 240), font=font)
        canvas.paste(im.resize((tw, TOP_H), Image.LANCZOS), (x, 52))
    y = 52 + TOP_H + 30
    for who, box in heads:
        d.text((20, y), f"{who}: recorte {box[2] - box[0]} px, x{CROP_W / (box[2] - box[0]):.1f}", fill=(200, 200, 205), font=small)
        for i, (im, lab) in enumerate(zip(imgs, labels)):
            crop = im.crop(box).resize((CROP_W, CROP_W), Image.NEAREST)
            canvas.paste(crop, (20 + i * ccol, y + 26))
        y += CROP_W + 50
    out = PROCESS / f"estilos-pared{'-piloto' if preview else ''}-{name}{'-' + tag if tag else ''}.png"
    canvas.save(out)
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    zoom = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--zoom=")), 2)
    boxes = [tuple(float(v) for v in a.split("=")[1].split(",")) for a in sys.argv if a.startswith("--box=")]
    tag = next((a.split("=")[1] for a in sys.argv if a.startswith("--name=")), "")
    print(main(args[0], "--preview" in sys.argv, zoom, boxes, tag))
