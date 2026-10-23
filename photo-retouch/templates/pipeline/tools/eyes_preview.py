"""Ojeras antes y despues, con la luz y el color finales: RAW revelado | retoque de piel | diferencia.

Corre solo el retoque de piel (skin.retouch_face) sobre la base, sin granos ni pelusas, y gradua
cada recorte como grade.py (sin el emparejado de la pared, que cerca de las caras es ~0).

Uso: .venv/bin/python tools/eyes_preview.py <foto> [...] -> proceso/31-ojeras/<foto>-antes-despues.png
     .venv/bin/python tools/eyes_preview.py <foto> --face <cara> --width 1100 -> <foto>-<cara>-cerca.png
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from common import PROCESS, linear_to_srgb, load_linear, luminance, to_uint8  # noqa: E402
from grade import EXPOSURE, color, sharpen, tone  # noqa: E402
from photos import PHOTOS  # noqa: E402
from skin import retouch_face  # noqa: E402

WIDTH = 640


def graded(part: np.ndarray) -> np.ndarray:
    return linear_to_srgb(sharpen(color(tone(part * EXPOSURE))))


def main(name: str, only: str | None = None, width: int = WIDTH) -> None:
    base = load_linear(name, "base")
    out = base.copy()
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 15)
    rows = []
    for face in PHOTOS[name]["faces"]:
        if only and face["id"] != only:
            continue
        print(face["id"], retouch_face(out, face).get("under_eyes"))
        pts = [p for eye in face["lids"] for p in eye]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        w = max(xs) - min(xs)
        x0, x1 = int(min(xs) - 0.15 * w), int(max(xs) + 0.15 * w)
        y0, y1 = int(min(ys) - 0.28 * w), int(max(ys) + 0.42 * w)
        a, b = base[y0:y1, x0:x1], out[y0:y1, x0:x1]
        d = np.log2(np.maximum(luminance(b), 1e-6) / np.maximum(luminance(a), 1e-6))
        panels = [graded(a), graded(b), np.dstack([np.clip(0.5 + 2 * d, 0, 1)] * 3).astype(np.float32)]
        zoom = width / (x1 - x0)
        if only:
            panels = panels[:2]
        ims = [to_uint8(cv2.resize(p, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_AREA if zoom < 1 else cv2.INTER_CUBIC), dither=False) for p in panels]
        gap = np.full((ims[0].shape[0], 6, 3), 20, np.uint8)
        row = Image.fromarray(np.concatenate([x for im in ims for x in (im, gap)][:-1], 1))
        dr = ImageDraw.Draw(row)
        for i, label in enumerate([f"{face['id']}: antes", "despues", "diferencia de luz x2"]):
            dr.text((i * (width + 6) + 8, 6), label, fill=(255, 40, 160), font=font)
        rows.append(np.asarray(row))
    h_gap = np.full((8, rows[0].shape[1], 3), 20, np.uint8)
    width = max(r.shape[1] for r in rows)
    rows = [np.pad(r, ((0, 0), (0, width - r.shape[1]), (0, 0))) for r in rows]
    sheet = np.concatenate([x for r in rows for x in (r, h_gap[:, :width])][:-1], 0)
    path = PROCESS / "31-ojeras" / (f"{name}-{only}-cerca.png" if only else f"{name}-antes-despues.png")
    Image.fromarray(sheet).save(path)
    print(path.name, sheet.shape[:2])


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="+")
    ap.add_argument("--face")
    ap.add_argument("--width", type=int, default=WIDTH)
    a = ap.parse_args()
    for n in a.names:
        main(n, a.face, a.width)
