"""Pared que el fondo nuevo no alcanzo: color de pared en la maestra y sin cambio en Bright white.

El blanco sube toda la pared al menos un 29 % (ganancia minima 1,29-1,44 en las cuatro), asi que un
pixel con color de pared que no cambio quedo del lado de la persona: un hueco entre el brazo y el
cuerpo, la pared entre las patas de la banqueta (piloto del 2026-10-15). Color de pared es respecto de
la luz de la pared en ese lugar (styles.wall_light), y en sombra hasta 25 L* mas oscuro.

No necesita el alpha: la persona es lo que el blanco dejo igual, asi que sirve igual para el piloto y
para las maestras. Desde que los estilos tambien ajustan la luz de la gente, "igual" es contra la maestra
con esos mismos ajustes y sin el fondo (lo que el fondo no toco), no contra la maestra.

Uso: .venv/bin/python tools/backdrop_holes.py <foto> --preview   (work/estilos/piloto/)
     .venv/bin/python tools/backdrop_holes.py <foto>             (editadas/)
Imprime cada zona y deja proceso/estilos-huecos[-piloto]-<foto>.png (maestra | zona en rojo | blanco)
y los numeros en proceso-notas/estilos/huecos[-piloto]-<foto>.json.
"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from common import EDITED, NOTES, PROCESS, lab, srgb_to_linear  # noqa: E402
from adjust import adjust, is_neutral  # noqa: E402
from backdrop import wall_light  # noqa: E402
from styles import PREVIEW, STYLES  # noqa: E402

FONT = "/System/Library/Fonts/Helvetica.ttc"
WALLISH = (25.0, 6.0, 2.5, 3.5)  # L* hasta 25 abajo y 6 arriba de la luz de la pared; |a*|, |b*|
SAME = 0.05  # cambio relativo por debajo del cual el blanco no toco el pixel
MIN_AREA = 7e-6  # zona minima, en fraccion de la foto (30 px a 2560)
TILE = 300


def load(path: Path) -> np.ndarray:
    with Image.open(path) as im:
        return np.asarray(im.convert("RGB"))


def find(master8: np.ndarray, white8: np.ndarray, light: dict) -> tuple[np.ndarray, list]:
    """Etiquetas y estadisticas (x, y, w, h, area) de cada zona, de mayor a menor. light: los ajustes de luz y
    color del blanco, que tambien mueven a la gente."""
    rgb = srgb_to_linear(master8.astype(np.float32) / 255)
    if not is_neutral(light):
        rgb = adjust(rgb, light)
    wht = srgb_to_linear(white8.astype(np.float32) / 255)
    lum = lambda x: x @ np.array([0.2126, 0.7152, 0.0722], np.float32)  # noqa: E731
    same = np.abs(lum(wht) - lum(rgb)) < SAME * np.maximum(lum(rgb), 1e-4)
    h, w = same.shape
    light = cv2.resize(wall_light(rgb, same.astype(np.float32)), (w, h), interpolation=cv2.INTER_LINEAR)
    d = lab(rgb) - lab(light)
    wallish = (d[..., 0] > -WALLISH[0]) & (d[..., 0] < WALLISH[1]) & (np.abs(d[..., 1]) < WALLISH[2]) & (np.abs(d[..., 2]) < WALLISH[3])
    miss = cv2.morphologyEx((wallish & same).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(miss)
    keep = [i for i in range(1, n) if stats[i, 4] >= MIN_AREA * h * w]
    return labels, sorted(((i, *map(int, stats[i])) for i in keep), key=lambda s: -s[5])


def main(name: str, preview: bool) -> dict:
    src = (PREVIEW / f"{name}-maestra.png", PREVIEW / f"{name}-white.png") if preview else (EDITED / f"{name}.png", EDITED / f"{name}-white.png")
    master8, white8 = load(src[0]), load(src[1])
    light = {k: v for k, v in STYLES["white"]["light"].items()}  # el resto de preset() es del fondo
    labels, zones = find(master8, white8, light)
    h, w = labels.shape
    report = {"photo": name, "size": [h, w], "zones": [{"box": [x, y, x + bw, y + bh], "area": a} for _, x, y, bw, bh, a in zones]}
    print(f"{name}: {len(zones)} zonas, {sum(z[5] for z in zones)} px")
    for _, x, y, bw, bh, a in zones[:12]:
        print(f"   x {x}-{x + bw} y {y}-{y + bh} area {a}  ({x / w:.2f},{y / h:.2f})-({(x + bw) / w:.2f},{(y + bh) / h:.2f})")
    tag = "-piloto" if preview else ""
    notes = NOTES / "estilos"
    notes.mkdir(parents=True, exist_ok=True)
    (notes / f"huecos{tag}-{name}.json").write_text(json.dumps(report, indent=1))
    font = ImageFont.truetype(FONT, 14)
    tiles = []
    for i, x, y, bw, bh, a in zones[:8]:
        side = max(bw, bh) + 60
        x0, y0 = max(0, x + bw // 2 - side // 2), max(0, y + bh // 2 - side // 2)
        box = (x0, y0, min(w, x0 + side), min(h, y0 + side))
        ov = master8.copy()
        m = labels == i
        ov[m] = (0.5 * ov[m] + [127, 0, 0]).astype(np.uint8)
        t = Image.new("RGB", (3 * TILE + 20, TILE + 22), (30, 30, 30))
        for j, im in enumerate((master8, ov, white8)):
            t.paste(Image.fromarray(im).crop(box).resize((TILE, TILE), Image.LANCZOS), (j * (TILE + 10), 22))
        ImageDraw.Draw(t).text((4, 3), f"x {x}-{x + bw} y {y}-{y + bh}, {a} px", fill=(220, 220, 220), font=font)
        tiles.append(t)
    if tiles:
        sheet = Image.new("RGB", (2 * (3 * TILE + 40), ((len(tiles) + 1) // 2) * (TILE + 32)), (20, 20, 20))
        for k, t in enumerate(tiles):
            sheet.paste(t, ((k % 2) * (3 * TILE + 40), (k // 2) * (TILE + 32)))
        out = PROCESS / f"estilos-huecos{tag}-{name}.png"
        sheet.save(out)
        print(out)
    return report


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for photo in args:
        main(photo, "--preview" in sys.argv)
