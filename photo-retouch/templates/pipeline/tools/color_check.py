"""Color de la piel y de la pared con distintas fuerzas del paso de color de grade.py.

Mide, por cara, la piel iluminada (mediana de L*, a*, b*, croma y tono) y su angulo en el
vectorscopio (Rec. 709, la linea de piel esta en ~123 grados), y en la pared el color que queda.
Las variantes son (croma, giro de la piel): sin paso de color, el actual y las que se pasen.

Hojas en proceso/40-color/: <foto>-piel-variantes.png (cada cara al 100 %, una columna por
variante) y <foto>-variantes.png (la foto entera chica).

Uso: .venv/bin/python tools/color_check.py <foto> [...] [--var 1.10,5 ...]
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
import grade  # noqa: E402
from common import PROCESS, lab, linear_to_srgb, load_linear, to_uint8  # noqa: E402
from develop import frac_box  # noqa: E402
from faces import ellipse_mask  # noqa: E402
from photos import PHOTOS  # noqa: E402
from wall import evening_gain  # noqa: E402

OUT = PROCESS / "40-color"
CROP = 420  # px de cara al 100 %
SMALL = 900  # ancho de la foto entera en la hoja


def graded(img: np.ndarray, chroma: float, hue: float) -> np.ndarray:
    grade.CHROMA, grade.SKIN_HUE = chroma, hue
    return grade.color(img) if (chroma, hue) != (1.0, 0.0) else img


def scope_angle(srgb: np.ndarray) -> np.ndarray:
    """Angulo en el vectorscopio (grados desde +Cb, antihorario), sobre el sRGB codificado."""
    y = srgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    cb = (srgb[..., 2] - y) / 1.8556
    cr = (srgb[..., 0] - y) / 1.5748
    return np.degrees(np.arctan2(cr, cb)) % 360


def skin_pixels(crop: np.ndarray, face: dict, origin) -> np.ndarray:
    """Piel iluminada de la cara: adentro del ovalo achicado, sin ojos/cejas/boca, ni sombra ni brillo."""
    cx, cy, rx, ry = face["oval"]
    inner = ellipse_mask(crop.shape[:2], [(cx, cy, rx * 0.7, ry * 0.7)], origin) > 0.5
    feats = ellipse_mask(crop.shape[:2], face["features"], origin, grow=1.4) > 0.5
    L, a, b = np.moveaxis(lab(crop), -1, 0)
    h = np.degrees(np.arctan2(b, a))
    c = np.hypot(a, b)
    return inner & ~feats & (L > 50) & (L < 88) & (c > 8) & (h > 15) & (h < 85)


def stats(lin: np.ndarray, m: np.ndarray) -> str:
    L, a, b = (np.median(v[m]) for v in np.moveaxis(lab(lin), -1, 0))
    ang = np.median(scope_angle(linear_to_srgb(lin))[m])
    return f"L {L:4.1f}  a {a:4.1f}  b {b:4.1f}  C {np.hypot(a, b):4.1f}  h {np.degrees(np.arctan2(b, a)):4.1f}  scope {ang:5.1f}"


def main(name: str, variants: list[tuple[float, float]]) -> None:
    img = load_linear(name, "retocada")
    img *= evening_gain(img, name)[..., None]
    img *= grade.EXPOSURE
    img = grade.tone(img)
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    faces = PHOTOS[name]["faces"]
    sheet = Image.new("RGB", (len(variants) * (CROP + 8) + 8, len(faces) * (CROP + 28) + 8), (16, 16, 16))
    d = ImageDraw.Draw(sheet)
    print(name)
    for i, face in enumerate(faces):
        cx, cy, rx, ry = face["oval"]
        y0, x0 = max(cy - ry, 0), max(cx - rx, 0)
        crop = img[y0 : cy + ry, x0 : cx + rx]
        m = skin_pixels(crop, face, (y0, x0))
        for j, (ch, hu) in enumerate(variants):
            out = graded(crop, ch, hu)
            print(f"  {face['id']:<11} {ch:.2f}/{hu:<3.0f} {stats(out, m)}")
            # el recorte: la mejilla y la nariz, al 100 %
            ty, tx = min(max(cy - y0 - CROP // 4, 0), out.shape[0] - CROP), min(max(cx - x0 - CROP // 2, 0), out.shape[1] - CROP)
            tile = to_uint8(linear_to_srgb(out[ty : ty + CROP, tx : tx + CROP]), dither=False)
            gx, gy = 8 + j * (CROP + 8), 8 + i * (CROP + 28)
            sheet.paste(Image.fromarray(tile), (gx, gy))
            d.text((gx, gy + CROP + 6), f"{face['id']}  croma x{ch:.2f}, piel +{hu:.0f}", fill=(220, 220, 220), font=font)
    for box in PHOTOS[name]["wall"]:
        wall = img[frac_box(box, img.shape[:2])][::4, ::4]
        for ch, hu in variants:
            a, b = np.median(lab(graded(wall, ch, hu))[..., 1:], axis=(0, 1))
            print(f"  pared {box}  {ch:.2f}/{hu:<3.0f} a {a:4.1f}  b {b:4.1f}")
    sheet.save(OUT / f"{name}-piel-variantes.png")
    small = cv2.resize(img, (SMALL, round(img.shape[0] * SMALL / img.shape[1])), interpolation=cv2.INTER_AREA)
    del img
    whole = Image.new("RGB", (len(variants) * (SMALL + 8) + 8, small.shape[0] + 36), (16, 16, 16))
    dw = ImageDraw.Draw(whole)
    for j, (ch, hu) in enumerate(variants):
        whole.paste(Image.fromarray(to_uint8(linear_to_srgb(graded(small, ch, hu)), dither=False)), (8 + j * (SMALL + 8), 8))
        dw.text((8 + j * (SMALL + 8), small.shape[0] + 14), f"croma x{ch:.2f}, piel +{hu:.0f}", fill=(220, 220, 220), font=font)
    whole.save(OUT / f"{name}-variantes.png")


if __name__ == "__main__":
    args = sys.argv[1:]
    extra = [tuple(float(v) for v in a.split(",")) for a in args[args.index("--var") + 1 :]] if "--var" in args else []
    names = args[: args.index("--var")] if "--var" in args else args
    for n in names:
        main(n, [(1.0, 0.0), (grade.CHROMA, grade.SKIN_HUE), *extra])
