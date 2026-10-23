"""Banco de pruebas de las ojeras, ojo por ojo: rapido, sobre recortes guardados.

1. cache: guarda cada cara tal como le llega a undereye.correct (granos curados, rojo y tono ya
   emparejados) en work/ojeras/<foto>-<cara>.npz, con la ganancia de la pared de ese recorte.
2. hoja: por cara, la cara entera a 50 % (antes | v2 | v3 a la intensidad de la final | v3 al
   100 % | v3 al 200 %, el tope del editor) y cada ojo de cerca (lo mismo, mas el aclarado y el
   color), graduado como grade.py y con el brillo ya bajado, como en la final. Debajo de cada ojo,
   los numeros de aceptacion:
   - falta: la luz que le falta a la ojera contra la piel esperada (percentil 90, en pasos), y
     cuanto queda despues de la v2 y de la v3 a cada intensidad. Tiene que quedar algo: la ojera es
     forma.
   - parpado: lo maximo que se aclaro en la franja de debajo de las pestanas. Tiene que ser 0.
   - textura: cuanto cambia el detalle fino (poros, grano). Tiene que ser ~0.
   - contorno: lo que cambia el aclarado de un pixel al siguiente por el borde de la zona (no por
     la ojera misma, que ya tiene su forma). Chico = sin contorno.
   - color: distancia de color entre la ojera y la piel de alrededor (log R/G y B/G, en %), sin
     importar el brillo, antes y despues.
   Los mapas de aclarado van en gris 50 % = nada, blanco = medio paso; el de color, x4.

Uso: .venv/bin/python tools/eyes_bench.py cache <foto> [...]
     .venv/bin/python tools/eyes_bench.py hoja <foto> [...] [--face <cara>]
     -> proceso/31-ojeras/v3/<foto>-<cara>.png
"""

import importlib.util
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
import undereye  # noqa: E402
from common import NOTES, PROCESS, WORK, blur, linear_to_srgb, load_linear, luminance, to_uint8  # noqa: E402
from faces import ellipse_mask, skin_mask, window  # noqa: E402
from grade import EXPOSURE, color, sharpen, tone  # noqa: E402
from heal import fix_hot, heal  # noqa: E402
from photos import PHOTOS  # noqa: E402
from skin import EDGE_FENCE, even_redness, even_tone, reduce_shine  # noqa: E402
from wall import evening_gain  # noqa: E402

CACHE = WORK / "ojeras"
OUT = PROCESS / "31-ojeras" / "v3"
EYE_W = 480  # ancho de cada panel de ojo
FONT = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
LEVELS = (undereye.INTENSITY, 1.0)  # la intensidad de la final y el 100 %; despues va el 200 % (otra capa)
TOP = "200 %"


def v2_module():
    path = NOTES / "31-ojeras" / "undereye-v2-suave.py.txt"
    sys.dont_write_bytecode = True  # sin __pycache__ al lado del codigo archivado
    spec = importlib.util.spec_from_loader("undereye_v2", importlib.machinery.SourceFileLoader("undereye_v2", str(path)))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cache(name: str) -> None:
    img = load_linear(name, "base")
    p = PHOTOS[name]
    for x, y, r in p.get("spots", []):
        heal(img, x, y, r)
    for x, y in p.get("hot", []):
        fix_hot(img, x, y, half=12)
    gain = evening_gain(img, name)
    CACHE.mkdir(parents=True, exist_ok=True)
    for face in p["faces"]:
        sy, sx = window(face, img.shape[:2])
        crop = img[sy, sx].copy()
        origin = (sy.start, sx.start)
        w = skin_mask(crop, face, origin, fence=EDGE_FENCE)
        crop = even_tone(even_redness(crop, w, face["oval"][2] / 12), w)
        np.savez(CACHE / f"{name}-{face['id']}.npz", crop=crop, origin=np.array(origin), w=w, gain=gain[sy, sx])
        print(f"{name}-{face['id']}: {crop.shape[1]}x{crop.shape[0]}")


def graded(crop: np.ndarray, w: np.ndarray, gain: np.ndarray, rx: float) -> np.ndarray:
    """Como en la final: el brillo se baja despues de las ojeras, y despues va grade.py."""
    c = reduce_shine(crop, w, rx / 8)
    return linear_to_srgb(sharpen(color(tone(c * gain[..., None] * EXPOSURE))))


def chroma_gap(crop: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
    """Distancia de color entre dos zonas sin importar el brillo: log(R/G) y log(B/G), en %."""
    rg = np.log(np.maximum(crop[..., 0], 1e-6) / np.maximum(crop[..., 1], 1e-6))
    bg = np.log(np.maximum(crop[..., 2], 1e-6) / np.maximum(crop[..., 1], 1e-6))
    return 100 * float(np.hypot(np.median(rg[a]) - np.median(rg[b]), np.median(bg[a]) - np.median(bg[b])))


def pct(t: float) -> str:
    return f"{round(100 * t)} %"


def numbers(crop: np.ndarray, out_v2: np.ndarray, outs: list, m: dict, face_level: float) -> dict:
    """`outs`: la v3 a cada intensidad de LEVELS y al 200 %."""
    zone, deficit, lift, width = m["zone"], m["deficit"], m["lift"], m["width"]
    core = zone > 0.5
    lift_v2 = np.log2(np.maximum(luminance(out_v2), 1e-7) / np.maximum(luminance(crop), 1e-7))
    ring = m["ring"] & (zone == 0)
    p90 = lambda a: float(np.percentile(a[core], 90)) if core.any() else 0.0  # noqa: E731
    # contorno: lo que cambia el aclarado por el borde de la zona (no por la ojera misma)
    gy, gx = np.gradient(zone)
    grow = undereye.MAX_LIFT * np.tanh(m["params"]["light"] * deficit / undereye.MAX_LIFT)
    lid_strip = (m["below"] > 0) & (m["below"] < undereye.LID_GAP * width)
    hp = lift - blur(lift, 1.5)
    return {
        "falta": p90(deficit),
        "queda": {"v2": p90(np.clip(deficit - lift_v2, 0, None))} | {pct(t): p90(np.clip(deficit - t * lift, 0, None)) for t in LEVELS}
        | {TOP: p90(np.clip(deficit - m["lift_top"], 0, None))},
        "tope": {"v2": float(np.where(zone > 0, lift_v2, 0).max())} | {pct(t): t * float(lift.max()) for t in LEVELS}
        | {TOP: float(m["lift_top"].max())},
        "parpado": float(lift[lid_strip].max()) if lid_strip.any() else 0.0,
        "textura": float(np.sqrt(np.mean(hp[zone > 0.05] ** 2))) if (zone > 0.05).any() else 0.0,
        "borde": float((np.hypot(gx, gy) * grow).max()),
        "color": {k: chroma_gap(c, core, ring) for k, c in zip(["antes", "v2", *map(pct, LEVELS), TOP], [crop, out_v2, *outs])},
        "lado": "luz" if float(np.median(luminance(crop)[ring])) >= face_level else "sombra",
    }


def summary(n: dict) -> str:
    each = lambda d: " | ".join(f"{k} {v:.2f}" for k, v in d.items())  # noqa: E731
    return (
        f"falta {n['falta']:.2f} EV; queda {each(n['queda'])}; tope {each(n['tope'])}; parpado {n['parpado']:.3f};"
        f" textura {n['textura']:.4f}; contorno {n['borde']:.4f} EV/px; color % {each(n['color'])}"
    )


def eye_box(face: dict, i: int, origin, depth: float) -> tuple[int, int, int, int]:
    oy, ox = origin
    pts = face["lids"][i]
    xs, ys = [p[0] - ox for p in pts], [p[1] - oy for p in pts]
    w = max(xs) - min(xs)
    return int(min(xs) - 0.35 * w), int(min(ys) - 0.35 * w), int(max(xs) + 0.35 * w), int(max(ys) + (depth + 0.3) * w)


def panel(img: np.ndarray, box, width: int) -> np.ndarray:
    x0, y0, x1, y1 = box
    part = img[max(y0, 0) : y1, max(x0, 0) : x1]
    zoom = width / part.shape[1]
    return to_uint8(cv2.resize(part, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_CUBIC if zoom > 1 else cv2.INTER_AREA), dither=False)


def label(im: np.ndarray, text: str) -> Image.Image:
    pim = Image.fromarray(im)
    ImageDraw.Draw(pim).text((8, 6), text, fill=(255, 40, 160), font=FONT)
    return pim


def sheet(name: str, face: dict, v2) -> dict:
    z = np.load(CACHE / f"{name}-{face['id']}.npz")
    crop, origin, w, gain = z["crop"], tuple(int(v) for v in z["origin"]), z["w"], z["gain"]
    rx = face["oval"][2]
    out_v2, _ = v2.correct(crop, face, origin)
    maps = undereye.eye_maps(crop, face, origin)
    layer = undereye.layers(maps)
    outs = [undereye.apply(crop, layer, t) for t in LEVELS] + [undereye.apply(crop, undereye.layers(maps, top=True))]
    views = [graded(c, w, gain, rx) for c in (crop, out_v2, *outs)]
    names = ["v2", *(f"v3 {pct(t)}" for t in LEVELS), f"v3 {TOP}"]
    lift_total = sum(m["lift"] for m in maps)
    lift_v2 = np.log2(np.maximum(luminance(out_v2), 1e-7) / np.maximum(luminance(crop), 1e-7))
    rows, report = [], []
    face_level = float(np.median(luminance(crop)[(ellipse_mask(crop.shape[:2], [face["oval"]], origin) > 0) & (w > 0.5)]))
    # la cara entera a 50 %: lo que se ve sin zoom
    half = [to_uint8(cv2.resize(v, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA), dither=False) for v in views]
    rows.append([label(h, t) for h, t in zip(half, ["antes (cara a 50 %)", *names])])
    for i, m in enumerate(maps):
        n = numbers(crop, out_v2, outs, m, face_level)
        n["ojo"] = i + 1
        n["params"] = m["params"]
        report.append(n)
        box = eye_box(face, i, origin, m["params"]["depth"])
        lift_im = np.dstack([np.clip(0.5 + lift_total, 0, 1)] * 3).astype(np.float32)
        lift_im = to_uint8(lift_im, dither=False)
        for mask, col in ((m["region"], (255, 40, 160)), (m["ring"], (60, 160, 255))):
            cnts, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(lift_im, cnts, -1, col, 1)
        tint = np.dstack([0.5 + 4 * sum(mm["tint"][0] for mm in maps), np.full(crop.shape[:2], 0.5), 0.5 + 4 * sum(mm["tint"][1] for mm in maps)])
        v2_im = to_uint8(np.dstack([np.clip(0.5 + lift_v2, 0, 1)] * 3).astype(np.float32), dither=False)
        cols = [panel(v, box, EYE_W) for v in views]
        cols += [panel(v2_im.astype(np.float32) / 255, box, EYE_W // 2), panel(lift_im.astype(np.float32) / 255, box, EYE_W // 2)]
        cols.append(panel(np.clip(tint, 0, 1).astype(np.float32), box, EYE_W // 2))
        texts = [f"ojo {i + 1}: antes", *names, "aclarado v2", "aclarado v3 100 %", "color v3 100 % (x4)"]
        rows.append([label(c, t) for c, t in zip(cols, texts)])
        caption = f"ojo {i + 1} ({n['lado']}): {summary(n)}"
        cap = Image.new("RGB", (sum(c.width for c in rows[-1]) + 6 * (len(rows[-1]) - 1), 26), (20, 20, 20))
        ImageDraw.Draw(cap).text((8, 5), caption, fill=(230, 230, 230), font=FONT)
        rows.append([cap])
    width = max(sum(p.width for p in r) + 6 * (len(r) - 1) for r in rows)
    height = sum(max(p.height for p in r) for r in rows) + 6 * (len(rows) - 1)
    out = Image.new("RGB", (width, height), (20, 20, 20))
    y = 0
    for r in rows:
        x = 0
        for p in r:
            out.paste(p, (x, y))
            x += p.width + 6
        y += max(p.height for p in r) + 6
    OUT.mkdir(parents=True, exist_ok=True)
    out.save(OUT / f"{name}-{face['id']}.png")
    # de cerca y sin mapas: antes | final | 100 % | 200 %, un ojo por fila, para mirar solo la piel
    close = [np.hstack([panel(views[k], eye_box(face, i, origin, maps[i]["params"]["depth"]), EYE_W) for k in (0, 2, 3, 4)]) for i in range(2)]
    width = max(c.shape[1] for c in close)
    Image.fromarray(np.vstack([np.pad(c, ((0, 6), (0, width - c.shape[1]), (0, 0)), constant_values=20) for c in close])).save(
        OUT / f"{name}-{face['id']}-cerca.png"
    )
    return {"foto": name, "cara": face["id"], "ojos": report}


def main() -> None:
    cmd, *rest = sys.argv[1:]
    only = rest[rest.index("--face") + 1] if "--face" in rest else None
    names = [n for n in rest if n in PHOTOS]  # las fotos: las claves de recipe/photos.py
    if cmd == "cache":
        for n in names:
            cache(n)
        return
    v2 = v2_module()
    reports = []
    for n in names:
        for face in PHOTOS[n]["faces"]:
            if only and face["id"] != only:
                continue
            r = sheet(n, face, v2)
            reports.append(r)
            for e in r["ojos"]:
                print(f"{n} {face['id']:<10} ojo {e['ojo']} ({e['lado']:<6}) {summary(e)}")
    numbers = NOTES / "31-ojeras" / "v3"
    numbers.mkdir(parents=True, exist_ok=True)
    (numbers / "numeros.json").write_text(json.dumps(reports, indent=1, default=float))


if __name__ == "__main__":
    main()
