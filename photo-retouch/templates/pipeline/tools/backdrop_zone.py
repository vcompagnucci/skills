"""Una zona de una foto en nativo, por estilo: sin fondo | maestra final | que cambio el fondo (dE, blanco = 4), y el alpha.

Para ver si el fondo toco algo de la gente (una zapatilla clara que el matting llamo pared) sin el ruido de
comparar contra otra version. "Sin fondo" es la maestra con la luz y el color del estilo (lo que el fondo no
toca); la final se lee de editadas/<foto>-<estilo>.tif.

Uso: .venv/bin/python tools/backdrop_zone.py <foto> 1440,5900,1680,6140 --name=zapatilla [--zoom=2]
Deja proceso/estilos-zona-<foto>-<nombre>.png e imprime, por estilo, cuantos px de gente (alpha 1) cambiaron.
"""

import sys
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
import backdrop  # noqa: E402
from adjust import TO_LINEAR, adjust_uint16  # noqa: E402
from common import EDITED, PROCESS, lab  # noqa: E402
from styles import STYLES, master, preset  # noqa: E402

FONT = "/System/Library/Fonts/Helvetica.ttc"
DE_WHITE, GAP, HEAD = 4.0, 8, 22


def to8(img16):
    return (img16.astype(np.float32) / 257 + 0.5).astype(np.uint8)


def main(name, box, zoom, tag):
    x0, y0, x1, y1 = box
    crop = master(name)[y0:y1, x0:x1]
    layers = backdrop.load_layers(name)
    a16 = layers.alpha16[y0:y1, x0:x1]
    rows = []
    for key in STYLES:
        light, _ = preset(name, key, layers)
        people = adjust_uint16(crop, light)
        final = tifffile.imread(EDITED / f"{name}-{key}.tif")[y0:y1, x0:x1]
        de = np.linalg.norm(lab(TO_LINEAR[final]) - lab(TO_LINEAR[people]), axis=-1)
        print(f"{key}: dE>2 en {(de > 2).sum()} px; con alpha 1 y cambio: {((a16 == 65535) & (final != people).any(-1)).sum()} px;"
              f" alpha<1 dentro de la zona: {(a16 < 65535).sum()} px")
        rows.append((STYLES[key]["name"], [to8(people), to8(final), np.repeat((np.clip(de / DE_WHITE, 0, 1) * 255).astype(np.uint8)[..., None], 3, -1)]))
    rows.append(("Alpha (blanco = persona)", [np.repeat(to8(a16)[..., None], 3, -1)]))
    labels = ["Sin fondo", "Final", f"Que cambio (blanco = dE {DE_WHITE:g})"]
    tw, th = (x1 - x0) * zoom, (y1 - y0) * zoom
    sheet = Image.new("RGB", (3 * tw + 4 * GAP, len(rows) * (th + HEAD + GAP) + GAP), (20, 20, 20))
    draw, font = ImageDraw.Draw(sheet), ImageFont.truetype(FONT, 14)
    for r, (title, imgs) in enumerate(rows):
        top = GAP + r * (th + HEAD + GAP)
        for c, img in enumerate(imgs):
            left = GAP + c * (tw + GAP)
            im = Image.fromarray(img)
            sheet.paste(im.resize((tw, th), Image.NEAREST), (left, top + HEAD))
            text = f"{title} - {labels[c]}" if len(imgs) > 1 else f"{title}, x {x0}-{x1} y {y0}-{y1}"
            draw.text((left + 2, top + 3), text, fill=(220, 220, 220), font=font)
    out = PROCESS / f"estilos-zona-{name}-{tag}.png"
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0], tuple(int(v) for v in args[1].split(",")), int(opts.get("zoom", 2)), opts.get("name", "zona"))
