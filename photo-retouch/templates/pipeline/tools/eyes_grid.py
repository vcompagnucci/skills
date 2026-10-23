"""Los dos ojos de cada cara con una grilla fina, para ubicar el parpado inferior y las ojeras.

Uso: .venv/bin/python tools/eyes_grid.py <foto> [...]  -> proceso/31-ojeras/<foto>-<cara>-grilla.png
     .venv/bin/python tools/eyes_grid.py --lids <foto> [...] -> <foto>-<cara>-parpados.png: cada ojo
     de cerca (grilla de 5 px), para leer la linea de pestanas de abajo.
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from common import PROCESS, linear_to_srgb, load_linear, luminance, to_uint8  # noqa: E402
from photos import PHOTOS  # noqa: E402

WIDTH = 1500


def main(name: str) -> None:
    img = load_linear(name, "base")
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    for face in PHOTOS[name]["faces"]:
        eyes = face["features"][:2]
        rx = max(e[2] for e in eyes)
        ry = max(e[3] for e in eyes)
        x0 = int(min(e[0] for e in eyes) - 1.5 * rx)
        x1 = int(max(e[0] for e in eyes) + 1.5 * rx)
        y0 = int(min(e[1] for e in eyes) - 1.6 * ry)
        y1 = int(max(e[1] for e in eyes) + 5.0 * ry)
        crop = img[y0:y1, x0:x1]
        # la cara a un gris medio, como en las hojas de candidatos
        k = 0.30 / max(float(np.median(luminance(crop))), 1e-6)
        zoom = WIDTH / (x1 - x0)
        srgb = cv2.resize(linear_to_srgb(crop * k), None, fx=zoom, fy=zoom, interpolation=cv2.INTER_CUBIC)
        im = Image.fromarray(to_uint8(srgb, dither=False))
        d = ImageDraw.Draw(im, "RGBA")
        step = 10
        for x in range((x0 // step + 1) * step, x1, step):
            major = x % 50 == 0
            px = (x - x0) * zoom
            d.line([(px, 0), (px, im.height)], fill=(0, 255, 255, 120 if major else 40))
            if major:
                d.text((px + 2, 2), str(x), fill=(0, 255, 255, 255), font=font)
        for y in range((y0 // step + 1) * step, y1, step):
            major = y % 50 == 0
            py = (y - y0) * zoom
            d.line([(0, py), (im.width, py)], fill=(255, 0, 255, 120 if major else 40))
            if major:
                d.text((2, py + 2), str(y), fill=(255, 0, 255, 255), font=font)
        for e in eyes:
            cx, cy, ex, ey = e[:4]
            ang = np.radians(e[4] if len(e) > 4 else 0)
            t = np.linspace(0, 2 * np.pi, 90)
            u, v = ex * np.cos(t), ey * np.sin(t)
            pts = [((cx + u_ * np.cos(ang) - v_ * np.sin(ang) - x0) * zoom, (cy + u_ * np.sin(ang) + v_ * np.cos(ang) - y0) * zoom) for u_, v_ in zip(u, v)]
            d.line(pts + [pts[0]], fill=(255, 214, 10, 200), width=1)
        out = PROCESS / "31-ojeras" / f"{name}-{face['id']}-grilla.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out)
        print(out.name, im.size, f"x {x0}-{x1} y {y0}-{y1} zoom {zoom:.2f}")


def lids(name: str) -> None:
    img = load_linear(name, "base")
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
    for face in PHOTOS[name]["faces"]:
        tiles = []
        for e in face["features"][:2]:
            cx, cy, rx, ry = e[:4]
            x0, x1 = int(cx - 1.35 * rx), int(cx + 1.35 * rx)
            y0, y1 = int(cy - 0.6 * ry), int(cy + 3.4 * ry)
            crop = img[y0:y1, x0:x1]
            k = 0.30 / max(float(np.median(luminance(crop))), 1e-6)
            zoom = 1100 / (x1 - x0)
            srgb = cv2.resize(linear_to_srgb(crop * k), None, fx=zoom, fy=zoom, interpolation=cv2.INTER_CUBIC)
            im = Image.fromarray(to_uint8(srgb, dither=False))
            d = ImageDraw.Draw(im, "RGBA")
            for x in range((x0 // 5 + 1) * 5, x1, 5):
                major = x % 10 == 0
                px = (x - x0) * zoom
                d.line([(px, 0), (px, im.height)], fill=(0, 255, 255, 110 if x % 50 == 0 else 60 if major else 22))
                if x % 20 == 0:
                    d.text((px + 2, 2), str(x), fill=(0, 255, 255, 255), font=font)
            for y in range((y0 // 5 + 1) * 5, y1, 5):
                major = y % 10 == 0
                py = (y - y0) * zoom
                d.line([(0, py), (im.width, py)], fill=(255, 0, 255, 110 if y % 50 == 0 else 60 if major else 22))
                if y % 10 == 0:
                    d.text((2, py + 1), str(y), fill=(255, 0, 255, 255), font=font)
            out = PROCESS / "31-ojeras" / f"{name}-{face['id']}-parpado-{len(tiles) + 1}.png"
            im.save(out)
            tiles.append(out)
            print(out.name, f"x {x0}-{x1} y {y0}-{y1}")


def zones_sheet(name: str) -> None:
    """La linea de pestanas medida (amarillo), la zona de la ojera (celeste, mitad de la mascara)
    y la mejilla de referencia (magenta), sobre cada ojo de cerca."""
    from faces import window
    from undereye import lid_curve, skin_weight, zones

    img = load_linear(name, "base")
    for face in PHOTOS[name]["faces"]:
        sy, sx = window(face, img.shape[:2])
        crop = img[sy, sx]
        origin = (sy.start, sx.start)
        skin = skin_weight(crop, face, origin)
        lids = face["lids"]
        tiles = []
        for i, (e, points) in enumerate(zip(face["features"][:2], lids)):
            other_x = float(np.mean([p[0] for p in lids[1 - i]]))
            zone, band = zones(crop.shape[:2], points, other_x, origin)
            zone = zone * skin
            lid = lid_curve(points, origin)
            cx, cy, rx, ry = e[0] - origin[1], e[1] - origin[0], e[2], e[3]
            x0, x1 = int(cx - 1.35 * rx), int(cx + 1.35 * rx)
            y0, y1 = int(cy - 0.6 * ry), int(cy + 3.6 * ry)
            part = crop[y0:y1, x0:x1]
            k = 0.30 / max(float(np.median(luminance(part))), 1e-6)
            zoom = 1100 / (x1 - x0)
            srgb = cv2.resize(linear_to_srgb(part * k), None, fx=zoom, fy=zoom, interpolation=cv2.INTER_CUBIC)
            rgb = to_uint8(srgb, dither=False)
            for m, color in ((zone[y0:y1, x0:x1] > 0.5, (100, 210, 255)), (band[y0:y1, x0:x1] > 0.5, (255, 55, 200))):
                mz = cv2.resize(m.astype(np.uint8), (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_NEAREST)
                edge = mz - cv2.erode(mz, np.ones((3, 3), np.uint8))
                rgb[edge > 0] = color
            im = Image.fromarray(rgb)
            d = ImageDraw.Draw(im)
            xs = np.arange(x0, x1)
            d.line([((x - x0) * zoom, (np.polyval(lid, x) - y0) * zoom) for x in xs], fill=(255, 214, 10), width=1)
            for px, py in points:
                qx, qy = (px - origin[1] - x0) * zoom, (py - origin[0] - y0) * zoom
                d.ellipse([qx - 4, qy - 4, qx + 4, qy + 4], outline=(255, 214, 10), width=2)
            tiles.append(np.asarray(im))
        h = max(t.shape[0] for t in tiles)
        tiles = [np.pad(t, ((0, h - t.shape[0]), (0, 0), (0, 0))) for t in tiles]
        out = PROCESS / "31-ojeras" / f"{name}-{face['id']}-zona.png"
        Image.fromarray(np.concatenate([tiles[0], np.full((h, 8, 3), 20, np.uint8), tiles[1]], 1)).save(out)
        print(out.name)


if __name__ == "__main__":
    args = sys.argv[1:]
    run = {"--lids": lids, "--zones": zones_sheet}.get(args[0], main) if args else main
    for n in [a for a in args if not a.startswith("--")]:
        run(n)
