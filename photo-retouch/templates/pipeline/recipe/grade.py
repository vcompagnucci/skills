"""Del retoque a la foto final: luz, curva, color y nitidez, en float sobre el RAW revelado.

1. Pared: la caida de luz del flash se empareja a medias (wall.evening_gain), como un filtro
   graduado sobre toda la foto. Sin mascaras: no puede dejar halos.
2. Exposicion: la misma para las cuatro (misma sesion, mismo flash, misma camara). La piel
   iluminada queda en L* ~70 antes de la curva y ~74 despues.
3. Curva: una S suave sobre L*, aplicada a la luminancia sin cambiar el tono de ningun color.
4. Color: +18 % de croma (el revelado colorimetrico sale apagado al lado de como se ve en
   persona) y el tono de piel 8 grados hacia el amarillo: el revelado lo deja en 40-49 grados,
   un poco rosado. Los neutros y los demas colores no se mueven. Medido con tools/color_check.py
   (2026-10-14): la piel iluminada queda a 120-126 grados en el vectorscopio (la linea de piel
   esta en ~123) con croma 19-21, y la pared en a*, b* ~0. Sin este paso queda en ~115, rosada;
   con +12 grados una de las caras se pasa al amarillo.
5. Nitidez de captura: suave, sobre la luminancia en escala log (bordes parejos, sin halo
   claro) y solo donde hay detalle: en la pared lisa subiria el ruido.

Salidas en editadas/: <foto>.tif (16 bits, sRGB con perfil) y <foto>.png (8 bits con dither),
mas <foto>-antes.png, el RAW tal como salio de la camara, para comparar.

Ojeras: la final las trae a la intensidad de undereye.INTENSITY. Para el control del editor salen
tambien las puntas, 0, 100 y 200 %, en parches chicos alrededor de cada ojera (editadas/ojeras/,
TIFF de 16 bits para exportar y PNG de 8 para mirar, con ojeras.json diciendo donde va cada uno).
Se arman desde la misma retocada sacando o completando la correccion, que es pura ganancia (el 200 %
saca la de la final y pone la suya, que es otra capa), y se gradua cada parche con margen (PAD) para
que la nitidez vea lo mismo que en la foto entera: afuera de la ojera, un parche es pixel por pixel
la final.

Uso: .venv/bin/python recipe/grade.py <foto> [...]
"""

import json
import sys

import numpy as np
from scipy.interpolate import PchipInterpolator

from common import (
    EDITED,
    WORK,
    blur,
    dither_noise,
    lab,
    lab_to_linear,
    lightness,
    lightness_to_y,
    linear_to_srgb,
    load_linear,
    luminance,
    save_png,
    save_tiff16,
)
from undereye import INTENSITY
from undereye import apply as under_eyes
from wall import evening_gain

EXPOSURE = 1.80  # +0,85 EV: la piel iluminada de L* ~55 a ~70
# curva sobre L* (entrada, salida): negros firmes sin aplastar la tela, medios con un poco mas
# de contraste, y las luces (la pared) un poco mas claras
CURVE = [(0, 0), (5, 4.2), (15, 13.5), (30, 29), (50, 51), (67, 70), (80, 84.5), (90, 93), (100, 100)]
CHROMA = 1.18
SKIN_HUE = 8.0  # grados hacia el amarillo, en el rango de la piel
SHARPEN = 0.35
STRIP = 512  # filas por tanda en los pasos de color (memoria)
EYES = EDITED / "ojeras"
MARGIN = 16  # alrededor de la capa de ojeras: hasta aca la nitidez puede mover un pixel
PAD = 32  # la nitidez mira ~15 px alrededor: el parche se gradua con esto de mas y se recorta
TOP = 200  # el tope del control del editor, en %: la punta del 200 % es la capa top de undereye

_curve = PchipInterpolator(*zip(*CURVE))


def tone(img: np.ndarray) -> np.ndarray:
    y = luminance(img)
    L = lightness(y)
    y_out = lightness_to_y(_curve(np.clip(L, 0, 100))).astype(np.float32)
    return img * (y_out / np.maximum(y, 1e-7))[..., None]


def skin_hue_weight(hue: np.ndarray) -> np.ndarray:
    """1 entre 30 y 60 grados (piel), bajando a 0 en 10 y en 85: labios a medias, nada mas."""
    rise = np.clip((hue - 10) / 20, 0, 1)
    fall = np.clip((85 - hue) / 25, 0, 1)
    return rise * fall


def color(img: np.ndarray) -> np.ndarray:
    out = np.empty_like(img)
    for y0 in range(0, img.shape[0], STRIP):
        part = lab(img[y0 : y0 + STRIP])
        a, b = part[..., 1], part[..., 2]
        hue = np.degrees(np.arctan2(b, a))
        turn = np.radians(SKIN_HUE * skin_hue_weight(hue))
        c, s = np.cos(turn), np.sin(turn)
        a2, b2 = (a * c - b * s) * CHROMA, (a * s + b * c) * CHROMA
        part[..., 1], part[..., 2] = a2, b2
        out[y0 : y0 + STRIP] = lab_to_linear(part)
    return out


def sharpen(img: np.ndarray) -> np.ndarray:
    y = np.maximum(luminance(img), 1e-6)
    lg = np.log2(y)
    detail = lg - blur(lg, 0.8)
    # donde hay textura de verdad (piel, tela, pelo): el ruido de la pared es mas chico que esto
    texture = np.sqrt(np.maximum(blur(detail**2, 3.0), 0))
    where = np.clip((texture - 0.03) / 0.04, 0, 1)
    gain = np.exp2(SHARPEN * detail * where)
    return img * gain[..., None]


def finish(img: np.ndarray, gain: np.ndarray) -> np.ndarray:
    """De la retocada lineal a sRGB: pared, exposicion, curva, color y nitidez. Cambia img."""
    img *= gain[..., None]
    img *= EXPOSURE
    img = tone(img)
    img = color(img)
    img = sharpen(img)
    return linear_to_srgb(img)


def eye_ends(name: str, img: np.ndarray, gain: np.ndarray) -> list[dict]:
    """Las puntas del control de ojeras (0, 100 y 200 %), en un parche por cara. img: la retocada."""
    path = WORK / f"{name}-ojeras.npz"
    if not path.exists():
        return []
    z = np.load(path)
    H, W = img.shape[:2]
    out = []
    for fid in (k for k in z.files if not k.endswith(("-origen", "-200"))):
        layer = z[fid]
        oy, ox = (int(v) for v in z[f"{fid}-origen"])
        h, w = layer.shape[:2]
        y0, x0, y1, x1 = max(oy - MARGIN, 0), max(ox - MARGIN, 0), min(oy + h + MARGIN, H), min(ox + w + MARGIN, W)
        Y0, X0, Y1, X1 = max(y0 - PAD, 0), max(x0 - PAD, 0), min(y1 + PAD, H), min(x1 + PAD, W)
        padded, top = (np.zeros((Y1 - Y0, X1 - X0, 3), np.float32) for _ in range(2))
        padded[oy - Y0 : oy - Y0 + h, ox - X0 : ox - X0 + w] = layer
        top[oy - Y0 : oy - Y0 + h, ox - X0 : ox - X0 + w] = z[f"{fid}-200"]
        inner = (slice(y0 - Y0, y1 - Y0), slice(x0 - X0, x1 - X0))
        part = img[Y0:Y1, X0:X1]
        # la final ya tiene INTENSITY: se saca entera (0 %), se completa (100 %), o se saca y va la del tope
        ends = {
            tag: finish(src, gain[Y0:Y1, X0:X1])[inner]
            for tag, src in (
                ("0", under_eyes(part, padded, -INTENSITY)),
                ("100", under_eyes(part, padded, 1 - INTENSITY)),
                ("200", under_eyes(under_eyes(part, padded, -INTENSITY), top)),
            )
        }
        out.append({"face": fid, "box": (x0, y0, x1 - x0, y1 - y0), "ends": ends})
    return out


def save_eye_ends(name: str, ends: list[dict], noise: np.ndarray) -> None:
    """Los parches, con el dither cortado del de la foto entera, y donde va cada uno."""
    entries = []
    for e in ends:
        x, y, w, h = e["box"]
        for tag, srgb in e["ends"].items():
            save_tiff16(srgb, EYES / f"{name}-{e['face']}-{tag}.tif")
            save_png(srgb, EYES / f"{name}-{e['face']}-{tag}.png", noise=noise[y : y + h, x : x + w])
        entries.append({"face": e["face"], "x": x, "y": y, "w": w, "h": h})
    manifest = EYES / "ojeras.json"
    photos = json.loads(manifest.read_text())["photos"] if manifest.exists() else {}
    photos[name] = entries
    manifest.write_text(json.dumps({"intensity": round(INTENSITY * 100), "max": TOP, "photos": photos}, indent=1))


def grade(name: str) -> tuple[np.ndarray, list[dict]]:
    img = load_linear(name, "retocada")
    gain = evening_gain(img, name)
    ends = eye_ends(name, img, gain)  # antes de finish, que cambia img
    return finish(img, gain), ends


def before(name: str) -> np.ndarray:
    return linear_to_srgb(load_linear(name, "antes"))


if __name__ == "__main__":
    for n in sys.argv[1:]:
        srgb, ends = grade(n)
        save_tiff16(srgb, EDITED / f"{n}.tif")
        noise = dither_noise(srgb.shape)
        save_png(srgb, EDITED / f"{n}.png", noise=noise)
        del srgb
        save_eye_ends(n, ends, noise)
        del noise, ends
        save_png(before(n), EDITED / f"{n}-antes.png")
        print(f"{n}: editadas/{n}.tif, {n}.png, {n}-antes.png y las puntas de las ojeras")
