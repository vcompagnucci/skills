"""La pared del matting (alpha < 0,5) pintada de rojo sobre la maestra: para buscar gente que el matting llamo
pared (el cuero de una zapatilla blanca en sombra, una suela, la banqueta) sin mirar recorte por recorte.
Correrlo cada vez que se rehacen las capas del fondo (styles.py --layers).

Uso: .venv/bin/python tools/backdrop_alpha_red.py <foto> [<otra> ...]          la foto entera, lado largo 2000 px
     .venv/bin/python tools/backdrop_alpha_red.py <foto> --box=1250,5250,2150,6246 --name=pies   una zona en nativo
Deja proceso/estilos-alpha-rojo-<foto>[-<nombre>].png. Con la foto entera imprime ademas las islas de pared que no
tocan el borde (x0, y0, x1, y1, area en px nativos), de mayor a menor: los huecos de verdad y lo que hay que mirar.
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
import backdrop  # noqa: E402
from common import EDITED, PROCESS  # noqa: E402

LONG = 2000
RED = np.array([235, 40, 40], np.float32)


def main(name: str, box=None, tag: str = "") -> Path:
    a16 = backdrop.load_layers(name).alpha16
    with Image.open(EDITED / f"{name}.png") as im:
        rgb = np.asarray(im.convert("RGB"))
    if box:
        x0, y0, x1, y1 = box
        wall = (a16[y0:y1, x0:x1] < 32768)[..., None]
        out = np.where(wall, rgb[y0:y1, x0:x1] * 0.45 + RED * 0.55, rgb[y0:y1, x0:x1])
    else:
        wall = (a16 < 32768).astype(np.uint8)
        _, _, stats, _ = cv2.connectedComponentsWithStats(wall, connectivity=8)
        H, W = wall.shape
        islands = sorted(((int(s[0]), int(s[1]), int(s[0] + s[2]), int(s[1] + s[3]), int(s[4])) for s in stats[1:]
                          if s[4] >= 50 and s[0] > 0 and s[1] > 0 and s[0] + s[2] < W and s[1] + s[3] < H), key=lambda i: -i[4])
        print(name, f"{len(islands)} islas", islands[:20])
        s = LONG / max(H, W)
        size = (round(W * s), round(H * s))
        w = cv2.resize(wall.astype(np.float32), size, interpolation=cv2.INTER_AREA)[..., None]
        out = cv2.resize(rgb, size, interpolation=cv2.INTER_AREA).astype(np.float32) * (1 - 0.55 * w) + RED * 0.55 * w
    path = PROCESS / f"estilos-alpha-rojo-{name}{'-' + tag if tag else ''}.png"
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(path)
    print(path)
    return path


if __name__ == "__main__":
    opts = dict(a[2:].split("=", 1) for a in sys.argv[1:] if a.startswith("--") and "=" in a)
    box = tuple(int(v) for v in opts["box"].split(",")) if "box" in opts else None
    for photo in (a for a in sys.argv[1:] if not a.startswith("--")):
        main(photo, box, opts.get("name", ""))
