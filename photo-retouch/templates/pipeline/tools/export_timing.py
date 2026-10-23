"""Cuanto tarda cada paso de una descarga, en el mismo codigo que el servidor (editor_server.prepare), y cuanto
cambian el tiempo y el peso las opciones de compresion sin perdida. Todo en memoria: nada se escribe en disco.

Uso: MallocLargeCache=0 nice -n 19 .venv/bin/python tools/export_timing.py
Numeros en proceso-notas/export/timing.json.
"""

import io
import json
import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import tifffile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "recipe"))
import adjust  # noqa: E402
import backdrop  # noqa: E402
import editor_server as es  # noqa: E402
from common import NOTES  # noqa: E402
from photos import STUDIO  # noqa: E402

PHOTO = os.environ.get("EDITOR_TEST_PHOTO") or STUDIO[0]  # una foto con pared y caras inventariadas
ADJUST = {"exposure": 0.29, "contrast": 5, "highlights": -20, "shadows": 20, "whites": -8, "blacks": -10, "vibrance": 10}
BG = {"exposure": 0.62, "evenness": 100, "smoothing": 100, "saturation": -100}
REPEAT = 2


def clock(fn, repeat=REPEAT):
    best, out = None, None
    for _ in range(repeat):
        t = time.perf_counter()
        out = fn()
        dt = time.perf_counter() - t
        best = dt if best is None else min(best, dt)
    return round(best, 3), out


def main() -> None:
    params = adjust.parse(ADJUST) if hasattr(adjust, "parse") else {**{k: 0 for k in adjust.KEYS}, **ADJUST}
    bg = backdrop.parse(BG)
    path, bits, sig = es.source(PHOTO, "edit")
    rows = {}
    t = time.perf_counter(); img = es.master(PHOTO, "edit", path, bits, sig); rows["master, cold"] = round(time.perf_counter() - t, 3)
    rows["master, cached"], _ = clock(lambda: es.master(PHOTO, "edit", path, bits, sig))
    H, W = img.shape[:2]
    t = time.perf_counter(); lay = es.layers(PHOTO, es.layer_sig(PHOTO)); rows["background layers, cold"] = round(time.perf_counter() - t, 3)
    manifest, _ = es.eye_manifest()
    rows["under-eyes blend (70 = default)"], crop = clock(lambda: es.blend_eyes(img, PHOTO, 0, 0, manifest["intensity"], manifest))
    rows["adjust only (no background)"], _ = clock(lambda: adjust.adjust_uint16(crop, params))
    rows["adjust + background"], full = clock(lambda: backdrop.render(crop, 0, 0, (H, W), lay, params, bg))
    rows["resample to 2048"], small = clock(lambda: es.resample(full, round(W * 2048 / max(W, H)), round(H * 2048 / max(W, H))))

    def png(img16, level):
        return cv2.imencode(".png", cv2.cvtColor(img16, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_PNG_COMPRESSION, level])[1].tobytes()

    def tiff(img16, level):
        buf = io.BytesIO()
        tifffile.imwrite(buf, img16, photometric="rgb", compression="zlib", compressionargs={"level": level}, predictor=True)
        return buf.getvalue()

    def webp(img8, method):
        buf = io.BytesIO(); Image.fromarray(img8).save(buf, "WEBP", lossless=True, quality=60, method=method, exact=True)
        return buf.getvalue()

    def lossy(img8, optimize):
        buf = io.BytesIO(); Image.fromarray(img8).save(buf, "JPEG", quality=95, subsampling=0, optimize=optimize, progressive=True)
        return buf.getvalue()

    to8 = lambda a: ((a.astype(np.uint32) + 128) // 257).astype(np.uint8)
    enc = {}
    for label, im in (("full", full), ("2048", small)):
        im8 = to8(im)
        for name, fn in (("png level 3 (today)", lambda: png(im, 3)), ("png level 1", lambda: png(im, 1)),
                         ("tiff zlib 3 (today)", lambda: tiff(im, 3)), ("tiff zlib 1", lambda: tiff(im, 1)),
                         ("webp method 4 (today)", lambda: webp(im8, 4)), ("webp method 1", lambda: webp(im8, 1)),
                         ("webp method 0", lambda: webp(im8, 0)),
                         ("jpg optimize (today)", lambda: lossy(im8, True)), ("jpg no optimize", lambda: lossy(im8, False))):
            dt, data = clock(fn, 1 if label == "full" else REPEAT)
            enc[f"{label} {name}"] = {"s": dt, "MB": round(len(data) / 1e6, 1)}
            print(f"{label:5} {name:24} {dt:6.2f} s  {len(data) / 1e6:6.1f} MB", flush=True)
    for k, v in rows.items():
        print(f"{k:34} {v:6.2f} s", flush=True)
    out = NOTES / "export" / "timing.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"photo": PHOTO, "steps": rows, "encode": enc}, indent=1))


if __name__ == "__main__":
    main()
