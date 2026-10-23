"""Piloto de un estilo: un juego de ajustes del editor sobre mis cuatro fotos, medido contra su referencia.

Mide con el mismo codigo que tools/ref_measure.py (measure), pero con las caras chicas (FACE_H px de
alto): el tono y el color no dependen de la escala, y asi cada vuelta tarda segundos. El grano si
depende de la escala, asi que aca no se mira.

Imprime, por foto, lo que un estilo mueve: la pared, la piel por percentil, su color y el negro, con la
referencia arriba. Y arma la hoja proceso/estilos-piloto-<ref>.png: la referencia y, por foto, la
entrega de hoy debajo y el estilo arriba.

Uso: .venv/bin/python tools/style_pilot.py <ref> '<ajustes json>'      (claves de recipe/adjust.py)
     .venv/bin/python tools/style_pilot.py <ref> '{"*": {...}, "<foto>": {...}}'   (lo de una foto pisa a "*")
     .venv/bin/python tools/style_pilot.py <ref> '<ajustes json>' --sheet
"""

import json
import sys
from pathlib import Path

import cv2
import numpy as np
import tifffile
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from adjust import KEYS, adjust, is_neutral, parse  # noqa: E402
from common import PHOTO_NAMES, PROCESS, ROOT, linear_to_srgb, to_uint8  # noqa: E402
from ref_measure import FONT, at_scale, measure, mine_regions, ref_regions  # noqa: E402
from references import load_reference  # noqa: E402

FACE_H = 360  # alto de cara al que se mide: chico para que cada vuelta tarde segundos
CACHE = ROOT / "work" / "estilos" / "cache"
SHEET_H = 520


def mine(name: str) -> np.ndarray:
    """La entrega achicada a caras de FACE_H px, guardada en work/ (se rehace si la maestra cambio)."""
    tif = ROOT / "editadas" / f"{name}.tif"
    path = CACHE / f"{name}-{FACE_H}.npy"
    if path.exists() and path.stat().st_mtime > tif.stat().st_mtime:
        return np.load(path)
    lin, _ = at_scale(name, FACE_H)
    CACHE.mkdir(parents=True, exist_ok=True)
    np.save(path, lin)
    return lin


def regions(name: str, lin: np.ndarray):
    """Las marcas de photos.py, a la escala de lo achicado."""
    with tifffile.TiffFile(ROOT / "editadas" / f"{name}.tif") as t:
        h, w = t.pages[0].shape[:2]
    return mine_regions(name, (h, w)).scaled(lin.shape[1] / w)


def line(tag: str, m: dict) -> str:
    w, s, b, t = m["wall"], m["skin"], m["black"], m["tone"]
    each = "/".join(f"{v:.0f}" for v in w["each"])
    return (f"{tag:9s} pared {each:>9s} a{w['a']:+4.1f} b{w['b']:+4.1f} | piel {s['p10']:3.0f} {s['p50']:3.0f} {s['p90']:3.0f} {s['p98']:3.0f}"
            f" a{s['a']:5.1f} b{s['b']:5.1f} C{s['C']:5.1f} h{s['h']:3.0f} | negro {b["p5"]:4.1f} {b["p50"]:4.1f} a{b["a"]:+4.1f} b{b["b"]:+4.1f} | p1 {t[0]:3.1f} p99 {t[4]:3.0f}")


def thumb(lin: np.ndarray, height: int) -> Image.Image:
    k = height / lin.shape[0]
    small = cv2.resize(lin, (round(lin.shape[1] * k), height), interpolation=cv2.INTER_AREA)
    return Image.fromarray(to_uint8(linear_to_srgb(np.clip(small, 0, 1)), dither=False))


def per_photo(raw: dict) -> dict[str, dict]:
    """Un juego para las cuatro, o "*" mas lo que cambia en alguna."""
    if set(raw) <= set(KEYS):
        raw = {"*": raw}
    return {n: parse(raw.get("*", {}) | raw.get(n, {})) for n in PHOTO_NAMES}


def main(ref: str, params: dict[str, dict], sheet: bool) -> None:
    ref_lin, ref_reg = load_reference(ref), ref_regions(ref)
    print(line("ref", measure(ref_lin, ref_reg)))
    before, after = [], []
    for name in PHOTO_NAMES:
        lin = mine(name)
        reg = regions(name, lin)
        out = lin if is_neutral(params[name]) else adjust(lin, params[name])
        print(line(name, measure(out, reg)))
        before.append(thumb(lin, SHEET_H))
        after.append(thumb(out, SHEET_H))
    if not sheet:
        return
    font = ImageFont.truetype(FONT, 18, index=1)
    r = thumb(ref_lin, SHEET_H)
    width = 20 + r.width + sum(im.width + 20 for im in after) + 20
    canvas = Image.new("RGB", (width, 2 * SHEET_H + 110), (24, 24, 26))
    d = ImageDraw.Draw(canvas)
    d.text((20, 12), f"Referencia: {ref}", fill=(240, 240, 240), font=font)
    canvas.paste(r, (20, 44))
    x = 40 + r.width
    for name, a, b in zip(PHOTO_NAMES, after, before):
        d.text((x, 12), f"{name}: estilo", fill=(240, 240, 240), font=font)
        canvas.paste(a, (x, 44))
        d.text((x, SHEET_H + 62), f"{name}: entrega de hoy", fill=(170, 170, 175), font=font)
        canvas.paste(b, (x, SHEET_H + 94))
        x += a.width + 20
    out = PROCESS / f"estilos-piloto-{ref}.png"
    canvas.save(out)
    print(out)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(args[0], per_photo(json.loads(args[1]) if len(args) > 1 else {}), "--sheet" in sys.argv)
