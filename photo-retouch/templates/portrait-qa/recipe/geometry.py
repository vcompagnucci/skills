"""Encuadres y recortes: de donde sale cada cuadrado y su mascara de fondo."""

import cv2
import numpy as np
import tifffile

from common import ROOT
from photos import PHOTOS

FRAMINGS = {
    "cerrado": "Cerrado, cara ~60 % (investigacion)",
    "medio": "Medio, como las referencias",
    "abierto": "Abierto, torso y manos",
}


def crop_box(name: str, framing: str) -> tuple[int, int, int]:
    if framing == "medio":
        return PHOTOS[name]["crop"]
    if framing == "abierto":
        return PHOTOS[name]["wide"]
    cx, cy, r = PHOTOS[name]["face"]
    side = int(3.7 * r)
    x0, y0 = int(cx - side / 2), int(cy + 0.3 * r - side / 2)
    return max(x0, 0), max(y0, 0), side


_FULL: dict[str, np.ndarray] = {}


def load_crop(name: str, framing: str, size: int) -> tuple[np.ndarray, tuple[float, float, float]]:
    """Recorte cuadrado lineal a `size` px y la cara en coordenadas del recorte."""
    x0, y0, side = crop_box(name, framing)
    if name not in _FULL:
        _FULL.clear()  # una foto entera por vez en memoria
        _FULL[name] = tifffile.imread(ROOT / "work" / f"{name}-retouched.tif")
    crop = _FULL[name][y0 : y0 + side, x0 : x0 + side].astype(np.float32) / 65535.0
    crop = cv2.resize(crop, (size, size), interpolation=cv2.INTER_AREA)
    cx, cy, r = PHOTOS[name]["face"]
    s = size / side
    return crop, ((cx - x0) * s, (cy - y0) * s, r * s)
