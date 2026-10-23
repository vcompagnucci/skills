"""Comprueba el export del editor contra el servidor que esta corriendo: cada formato x tamano x recorte.

Por combinacion pide el archivo a /api/prepare (lo mismo que manda el editor) y mira el archivo que llega, en memoria
(nunca se escribe a disco: el proyecto es .sin-jpg y el JPG solo sale por la descarga):
  - medidas: las que dice el editor (el lado largo del recorte al tamano pedido, nunca agrandado);
  - formato real del archivo, extension del nombre y bits (16 en PNG y TIFF, 8 en WebP y JPG);
  - perfil de color: sRGB marcado (bloque sRGB en PNG, ICC en los demas);
  - pixeles: contra la referencia, el PNG de 16 bits de la foto entera con los mismos ajustes, recortado al mismo marco
    y achicado igual que el servidor (en luz lineal). Diferencia en niveles de 8 bits: media y percentil 99.

Uso: MallocLargeCache=0 nice -n 19 .venv/bin/python tools/export_check.py [puerto]
Numeros en proceso-notas/export/check.json.
"""

import io
import json
import os
import struct
import sys
import urllib.request
from pathlib import Path

import cv2
import numpy as np
import tifffile
from PIL import Image, ImageCms

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "recipe"))
from adjust import TO_LINEAR  # noqa: E402
from common import EDITED, NOTES, linear_to_srgb  # noqa: E402
from photos import STUDIO  # noqa: E402

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8775
# la foto: EDITOR_TEST_PHOTO, o la primera de la sesion; sus medidas salen de la maestra (editadas/<foto>.tif)
PHOTO = os.environ.get("EDITOR_TEST_PHOTO") or STUDIO[0]
H, W = tifffile.TiffFile(EDITED / f"{PHOTO}.tif").pages[0].shape[:2]
_H169 = min(round(W * 9 / 16), H)
# ajustes y fondo de verdad (los de "Deep blacks, grey wall" con la pared tocada), para que el export los aplique
ADJUST = {"exposure": 0.29, "contrast": 15, "highlights": -20, "shadows": 10, "whites": -8, "blacks": -15, "vibrance": 12}
BACKGROUND = {"exposure": 0.2, "evenness": 50, "smoothing": 100}
CROPS = {"whole": [0, 0, W, H], "free": [round(W * 0.12), round(H * 0.11), round(W * 0.72), round(H * 0.67)],
         "16:9": [0, (H - _H169) // 4, W, _H169]}
SIZES = [1024, 2048, "full"]
FORMATS = {"png": (16, "PNG", ".png"), "tiff": (16, "TIFF", ".tif"), "webp": (8, "WEBP", ".webp"), "jpeg": (8, "JPEG", ".jpg")}
LIMIT = {"png": (0.05, 1), "tiff": (0.05, 1), "webp": (0.6, 1), "jpeg": (1.5, 6)}  # media y p99 maximos, niveles de 8 bits


def fetch(fmt: str, box: list, size) -> tuple[dict, bytes]:
    body = {"photo": PHOTO, "image": "edit", "box": box, "size": size, "format": fmt, "under_eyes": 70,
            "adjust": ADJUST, "background": BACKGROUND, "version": "Export check"}
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/api/prepare", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    meta = json.load(urllib.request.urlopen(req, timeout=600))
    data = urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/file/{meta['id']}", timeout=600).read()
    return meta, data


def expected(box: list, size) -> tuple[int, int]:
    w, h = box[2], box[3]
    long = max(w, h)
    out = long if size == "full" else min(size, long)
    return max(1, round(w * out / long)), max(1, round(h * out / long))


def is_srgb(icc: bytes | None) -> bool:
    """El perfil que trae el archivo es sRGB: lo dice su descripcion (la del perfil de Pillow es "sRGB built-in")."""
    if not icc:
        return False
    return "sRGB" in ImageCms.getProfileDescription(ImageCms.ImageCmsProfile(io.BytesIO(icc)))


def decode(fmt: str, data: bytes) -> tuple[np.ndarray, int, bool, str]:
    """pixeles uint16 (0-65535), bits del archivo, si marca sRGB, y el formato que dice el propio archivo"""
    if fmt == "tiff":
        with tifffile.TiffFile(io.BytesIO(data)) as t:
            img, icc = t.asarray(), t.pages[0].tags.get("InterColorProfile")
        bits = 16 if img.dtype == np.uint16 else 8
        return img.astype(np.uint16) * (1 if bits == 16 else 257), bits, is_srgb(icc and bytes(icc.value)), "TIFF"
    if fmt == "png":
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_UNCHANGED)
        bits = 16 if img.dtype == np.uint16 else 8
        srgb = b"sRGB" in data[:200] or b"iCCP" in data[:400]
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.uint16) * (1 if bits == 16 else 257), bits, srgb, "PNG"
    im = Image.open(io.BytesIO(data))
    srgb = is_srgb(im.info.get("icc_profile"))
    return np.asarray(im.convert("RGB")).astype(np.uint16) * 257, 8, srgb, im.format


def reference_part(ref16: np.ndarray, box: list, w: int, h: int) -> np.ndarray:
    x, y, bw, bh = box
    crop = ref16[y:y + bh, x:x + bw]
    if (bw, bh) == (w, h):
        return crop
    return (linear_to_srgb(cv2.resize(TO_LINEAR[crop], (w, h), interpolation=cv2.INTER_AREA)) * 65535 + 0.5).astype(np.uint16)


def main() -> None:
    meta, data = fetch("png", CROPS["whole"], "full")
    ref16, *_ = decode("png", data)
    del data
    print(f"referencia {meta['name']} {ref16.shape[1]} x {ref16.shape[0]}", flush=True)
    rows, failed = [], 0
    for crop_name, box in CROPS.items():
        for size in SIZES:
            for fmt, (want_bits, want_kind, ext) in FORMATS.items():
                meta, data = fetch(fmt, box, size)
                img, bits, srgb, kind = decode(fmt, data)
                ew, eh = expected(box, size)
                ref = reference_part(ref16, box, ew, eh)
                same_size = img.shape[:2] == (eh, ew)
                diff = np.abs(img.astype(np.int32) - ref.astype(np.int32)) / 257 if same_size else None
                mean = round(float(diff.mean()), 3) if same_size else None
                p99 = round(float(np.percentile(diff, 99)), 2) if same_size else None
                max_mean, max_p99 = LIMIT[fmt]
                checks = {
                    "size": same_size and (meta["w"], meta["h"]) == (ew, eh),
                    "format": kind == want_kind and meta["name"].endswith(ext),
                    "bits": bits == want_bits == meta["bits"],
                    "srgb": srgb,
                    "pixels": same_size and mean <= max_mean and p99 <= max_p99,
                }
                ok = all(checks.values())
                failed += not ok
                row = {"crop": crop_name, "size": size, "format": fmt, "name": meta["name"], "w": img.shape[1], "h": img.shape[0],
                       "bits": bits, "mb": round(len(data) / 1e6, 1), "diff_mean": mean, "diff_p99": p99, "checks": checks, "ok": ok}
                rows.append(row)
                bad = ", ".join(k for k, v in checks.items() if not v)
                print(f"{'ok ' if ok else 'MAL'} {crop_name:6} {str(size):5} {fmt:5} {row['w']:>5}x{row['h']:<5} {bits:>2}b "
                      f"{row['mb']:>6} MB  diff {mean} / p99 {p99}  {meta['name']}{'  <- ' + bad if bad else ''}", flush=True)
                del img, ref, data
    out = NOTES / "export" / "check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"port": PORT, "photo": PHOTO, "rows": rows}, indent=1))
    print(f"\n{len(rows) - failed} de {len(rows)} bien")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
