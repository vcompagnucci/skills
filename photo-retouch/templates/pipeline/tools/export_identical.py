"""Huellas de los pixeles que da editor_server.prepare (en proceso, sin servidor), para probar que un cambio de
velocidad no movio ni un bit. Decodifica cada archivo y hashea sus pixeles: la compresion puede cambiar, los pixeles no.

Uso: MallocLargeCache=0 nice -n 19 .venv/bin/python tools/export_identical.py <salida.json> [contra.json]
Con contra.json, compara y sale con 1 si algun caso difiere.
"""

import hashlib
import io
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import tifffile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "recipe"))
import editor_server as es  # noqa: E402
from photos import STUDIO  # noqa: E402

ADJUST = {"exposure": 0.29, "contrast": 5, "highlights": -20, "shadows": 20, "whites": -8, "blacks": -10, "vibrance": 10}
BG = {"exposure": 0.62, "evenness": 100, "smoothing": 100, "saturation": -100}
# las fotos: las tres primeras de la sesion (recipe/photos.py); con menos, se repiten. Los recortes van en fracciones
# del ancho y el alto de la maestra (x0, y0, ancho, alto), asi sirven en cualquier foto
_P = [*STUDIO, *STUDIO, *STUDIO][:3]
CASES = [  # foto, recorte (None = entera), tamano, formato, fondo
    (_P[0], None, "full", "png", True),
    (_P[0], None, "full", "tiff", True),
    (_P[0], None, 2048, "webp", True),
    (_P[0], (0.10, 0.22, 0.38, 0.38), "full", "png", True),
    (_P[0], (0.10, 0.22, 0.38, 0.38), 1024, "jpeg", True),
    (_P[1], (0, 0, 1, 0.375), 2048, "png", True),
    (_P[2], None, 1024, "png", False),
]


def pixels(fmt: str, data: bytes) -> np.ndarray:
    if fmt == "png":
        return cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_UNCHANGED)
    if fmt == "tiff":
        return tifffile.imread(io.BytesIO(data))
    return np.asarray(Image.open(io.BytesIO(data)).convert("RGB"))


def main() -> None:
    out, rows = sys.argv[1], {}
    for photo, box, size, fmt, bg in CASES:
        path, bits, sig = es.source(photo, "edit")
        W, H = es.master(photo, "edit", path, bits, sig).shape[1::-1]
        b = [round(f * d) for f, d in zip(box, (W, H, W, H))] if box else [0, 0, W, H]
        req = {"photo": photo, "image": "edit", "box": b, "size": size, "format": fmt, "under_eyes": 70, "adjust": ADJUST,
               "background": BG if bg else {}, "version": "identical"}
        t = time.perf_counter()
        meta = es.prepare(req, es.take_ticket())
        dt = time.perf_counter() - t
        data = es.files[meta["id"]][0]
        px = pixels(fmt, data)
        key = f"{photo} {b} {size} {fmt} bg={bg}"
        rows[key] = {"sha": hashlib.sha256(px.tobytes()).hexdigest(), "shape": list(px.shape), "dtype": str(px.dtype),
                     "MB": round(len(data) / 1e6, 1), "s": round(dt, 2)}
        print(f"{dt:6.2f} s  {len(data) / 1e6:6.1f} MB  {key}", flush=True)
    Path(out).write_text(json.dumps(rows, indent=1))
    if len(sys.argv) > 2:
        ref = json.loads(Path(sys.argv[2]).read_text())
        bad = [k for k in rows if rows[k]["sha"] != ref.get(k, {}).get("sha")]
        print("pixeles identicos en todos los casos" if not bad else f"DIFIEREN: {bad}")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
