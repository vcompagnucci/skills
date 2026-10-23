"""Revela cada RAF a una base lineal float (primarios sRGB, D65), y el "antes" del editor.

- Base (`work/<foto>-base.tif`, float16): el punto de partida de toda la edicion. El balance
  de blancos se mide en la pared gris del estudio y se aplica en el espacio de la camara,
  antes del demosaico (el demosaico de X-Trans interpola mejor sobre datos ya balanceados).
  La matriz camara -> sRGB se aplica aca en float, sin recortar: en el sensor no hay ningun
  pixel quemado (la pared llega al 30 % del blanco), asi que no se pierde nada.
- Antes (`work/<foto>-antes.tif`): el RAW tal como lo saco la camara, con su balance de
  blancos "as shot", sin curva y sin retoque. Solo se lo lleva a un brillo visible: el pixel
  mas claro queda en 0,95, como el "Camera original" del editor anterior.

Mismo demosaico, recorte y rotacion en las dos: el antes y el despues quedan alineados al pixel.

Uso: .venv/bin/python recipe/develop.py <foto> [<otra> ...]
"""

import sys

import numpy as np
import rawpy

from common import PHOTO_NAMES, ROOT, luminance, save_linear
from photos import PHOTOS

# sRGB (D65) -> XYZ, la misma tabla que usa LibRaw
XYZ_RGB = np.array(
    [[0.412453, 0.357580, 0.180423], [0.212671, 0.715160, 0.072169], [0.019334, 0.119193, 0.950227]]
)


def rgb_cam(raw: rawpy.RawPy) -> np.ndarray:
    """Camara (balanceada) -> sRGB lineal, como LibRaw: filas normalizadas para que el blanco quede blanco."""
    cam_xyz = np.asarray(raw.rgb_xyz_matrix[:3], np.float64)
    cam_rgb = cam_xyz @ XYZ_RGB
    cam_rgb /= cam_rgb.sum(axis=1, keepdims=True)
    return np.linalg.inv(cam_rgb).astype(np.float32)


def demosaic(raw: rawpy.RawPy, wb: list[float]) -> np.ndarray:
    """Camara RGB balanceada, lineal, en fraccion del blanco del sensor (canal verde = 1)."""
    rgb = raw.postprocess(
        demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,  # en X-Trans LibRaw usa Markesteijn de 3 pasadas
        user_wb=wb,
        output_color=rawpy.ColorSpace.raw,
        no_auto_bright=True,
        gamma=(1, 1),
        output_bps=16,
        highlight_mode=rawpy.HighlightMode.Clip,
        user_flip=None,
    )
    # LibRaw escala para que el multiplicador mas chico (el verde) lleve el blanco a 65535
    return rgb.astype(np.float32) / 65535.0


def frac_box(box: tuple[float, float, float, float], shape: tuple[int, int]) -> tuple[slice, slice]:
    y0, y1, x0, x1 = box
    h, w = shape
    return slice(int(y0 * h), int(y1 * h)), slice(int(x0 * w), int(x1 * w))


def wall_white_balance(raw: rawpy.RawPy, name: str) -> list[float]:
    """Multiplicadores que dejan la pared neutra, medidos en camara RGB sin balancear (media resolucion)."""
    cam = raw.postprocess(
        half_size=True, user_wb=[1, 1, 1, 1], output_color=rawpy.ColorSpace.raw,
        no_auto_bright=True, gamma=(1, 1), output_bps=16, highlight_mode=rawpy.HighlightMode.Clip,
    ).astype(np.float32)
    samples = []
    for box in PHOTOS[name]["wall"]:
        ys, xs = frac_box(box, cam.shape[:2])
        samples.append(np.median(cam[ys, xs].reshape(-1, 3), axis=0))
    med = np.median(np.array(samples), axis=0)
    return [float(med[1] / med[0]), 1.0, float(med[1] / med[2]), 1.0]


def develop(name: str) -> None:
    path = str(ROOT / "originales" / f"{name}.RAF")
    with rawpy.imread(path) as raw:
        matrix = rgb_cam(raw)
        shot = list(np.array(raw.camera_whitebalance[:3]) / raw.camera_whitebalance[1]) + [1.0]
        # sin `wall` en photos.py (la primera pasada, antes de poder leer la pared sobre un revelado), el balance de la
        # camara: sirve para leer los parches en tools/grid.py; despues se llena `wall` y se revela de nuevo
        wb = wall_white_balance(raw, name) if PHOTOS.get(name, {}).get("wall") else shot
        base = demosaic(raw, wb) @ matrix.T
    with rawpy.imread(path) as raw:
        before = demosaic(raw, shot) @ matrix.T

    save_linear(base, name, "base")
    # el antes: brillo visible sin recortar nada, sin curva
    gain = 0.95 / np.percentile(before.max(axis=2), 99.995)
    save_linear(before * gain, name, "antes")

    y = luminance(base)
    out_of_gamut = ((base < -0.002) | (base > 1)).any(axis=2).mean() * 100
    print(
        f"{name}: {base.shape[1]}x{base.shape[0]}  balance {'pared' if wb is not shot else 'de la camara (falta wall)'} R {wb[0]:.3f} B {wb[2]:.3f} "
        f"(camara R {shot[0]:.3f} B {shot[2]:.3f})  luminancia p50 {np.percentile(y, 50):.3f} "
        f"p99.9 {np.percentile(y, 99.9):.3f}  fuera de sRGB {out_of_gamut:.3f}%  antes x{gain:.2f}"
    )


if __name__ == "__main__":
    for n in sys.argv[1:] or PHOTO_NAMES:
        develop(n)
