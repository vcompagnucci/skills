"""Mide una referencia de estilo y mis fotos con el mismo codigo, con las caras al mismo tamano.

Todo en CIELAB (D65) sobre el sRGB de cada imagen:
- tono de la foto entera: L* en los percentiles 1, 5, 50, 95 y 99;
- pared: L*, a* y b* (la mediana de cada recuadro) y cuanto cambia de un recuadro a otro (la caida de
  luz o la vineta);
- piel: L* de la sombra (p10), el medio (p50), la luz (p90) y el techo (p98), y su color por franja de
  brillo (a*, b*, croma y matiz). La piel real es mas roja en la sombra y mas amarilla en la luz, y un
  promedio solo esconde una sombra de otro color;
- ropa negra: el negro de verdad (L* p5 y p50) y su tinte (a*, b*);
- grano: el desvio de L* menos su desenfoque, sobre la pared;
- recorte: clip %, el % de pixeles con algun canal en el codigo maximo del archivo (65535 en 16 bits, 255 en 8),
  contado sobre el archivo entero antes de achicarlo (achicar promedia el recorte y lo esconde). Se imprime por
  imagen y va a la hoja y al JSON.

Las referencias van en recipe/references.py, con sus caras, pared y ropa negra marcadas a mano; mis
fotos usan photos.py. Para comparar, mi foto se achica hasta que sus caras tengan el alto de las de la
referencia: una referencia chica no tiene detalle fino, y medir mas fino mediria la captura y no el
estilo.

Uso: .venv/bin/python tools/ref_measure.py <ref> [fotos...]
     cada foto es <foto> (la maestra), <foto>-<estilo> (la maestra de un estilo) o <foto>-antes (el revelado de la
     camara que escribe grade.py, la referencia de todo lo que un estilo no cambia)
     -> proceso/estilos-medida-<ref>.png y proceso-notas/estilos/medida-<ref>.json; imprime "clip % <imagen>: <valor>" por imagen
"""

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
import tifffile
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
from adjust import adjust  # noqa: E402
from common import EDITED, NOTES, PHOTO_NAMES, PROCESS, lab, linear_to_srgb, srgb_to_linear, to_uint8  # noqa: E402
from develop import frac_box  # noqa: E402
from photos import PHOTOS  # noqa: E402
from references import REFS, load_reference, ref_path  # noqa: E402

SKIN_BANDS = [(20, 40), (40, 55), (55, 65), (65, 75), (75, 85), (85, 97)]
MIN_BAND_PX = 60
FACE_SHRINK = 0.8  # la elipse achicada: sin el borde de la cara, que tiene pelo y pared
GRAIN_SIGMA = 1.5  # px a la escala medida
SHEET_H = 760  # alto de cada imagen en la hoja
FONT = "/System/Library/Fonts/Helvetica.ttc"


@dataclass
class Regions:
    faces: list = field(default_factory=list)  # (cx, cy, rx, ry)
    walls: list = field(default_factory=list)  # (x0, y0, x1, y1)
    blacks: list = field(default_factory=list)  # (x0, y0, x1, y1)

    def scaled(self, k: float) -> "Regions":
        return Regions([tuple(v * k for v in f) for f in self.faces],
                       [tuple(v * k for v in b) for b in self.walls],
                       [tuple(v * k for v in b) for b in self.blacks])

    def face_height(self) -> float:
        return float(np.mean([f[3] for f in self.faces]))


def photo_key(name: str) -> str:
    """La clave de photos.py de <foto>, <foto>-<estilo> o <foto>-antes: la mas larga que calce (hay claves con guiones)."""
    if name in PHOTOS:
        return name
    keys = [k for k in PHOTOS if name.startswith(k + "-")]
    if not keys:
        raise SystemExit(f"{name}: no es <foto>, <foto>-<estilo> ni <foto>-antes de una foto de recipe/photos.py")
    return max(keys, key=len)


def mine_regions(name: str, shape: tuple[int, int]) -> Regions:
    p = PHOTOS[photo_key(name)]
    walls = []
    for box in p["wall"]:
        sy, sx = frac_box(box, shape)
        walls.append((sx.start, sy.start, sx.stop, sy.stop))
    return Regions([f["oval"][:4] for f in p["faces"]], walls, list(p.get("blacks", [])))


def ref_regions(ref: str) -> Regions:
    r = REFS[ref]
    return Regions(list(r["faces"]), list(r["walls"]), list(r.get("blacks", [])))


def ellipses(shape: tuple[int, int], faces: list, shrink: float) -> np.ndarray:
    m = np.zeros(shape, np.uint8)
    for cx, cy, rx, ry in faces:
        cv2.ellipse(m, (round(cx), round(cy)), (max(1, round(rx * shrink)), max(1, round(ry * shrink))), 0, 0, 360, 1, -1)
    return m > 0


def upper_face(shape: tuple[int, int], faces: list) -> np.ndarray:
    """La cara hasta la punta de la nariz: frente, pomulos y nariz. Abajo hay vello facial, boca y menton, y un
    vello facial cerrado se media como piel en sombra."""
    m = np.zeros(shape, bool)
    for cx, cy, rx, ry in faces:
        rows = slice(max(0, round(cy - ry)), max(0, round(cy + 0.1 * ry)))
        cols = slice(max(0, round(cx - rx)), round(cx + rx))
        m[rows, cols] = True
    return m


def boxes(shape: tuple[int, int], rects: list, erode: int = 0) -> list[tuple[slice, slice]]:
    out = []
    for x0, y0, x1, y1 in rects:
        sy = slice(max(0, round(y0) + erode), min(shape[0], round(y1) - erode))
        sx = slice(max(0, round(x0) + erode), min(shape[1], round(x1) - erode))
        if sy.stop > sy.start and sx.stop > sx.start:
            out.append((sy, sx))
    return out


def hue(a: float, b: float) -> float:
    return float(np.degrees(np.arctan2(b, a)) % 360)


def measure(lin: np.ndarray, reg: Regions) -> dict:
    """lin: luz lineal float32 (h, w, 3) a la escala a comparar; reg en esa misma escala."""
    Lab = lab(lin)
    L, a, b = Lab[..., 0], Lab[..., 1], Lab[..., 2]
    C = np.hypot(a, b)
    h = np.degrees(np.arctan2(b, a)) % 360
    out = {"tone": [float(v) for v in np.percentile(L, [1, 5, 50, 95, 99])]}

    walls = [(float(np.median(L[s])), float(np.median(a[s])), float(np.median(b[s]))) for s in boxes(L.shape, reg.walls)]
    if walls:
        w = np.array(walls)
        out["wall"] = {"L": float(w[:, 0].mean()), "a": float(w[:, 1].mean()), "b": float(w[:, 2].mean()),
                       "spread": float(w[:, 0].max() - w[:, 0].min()), "each": [round(v, 1) for v in w[:, 0]]}
        core = np.zeros(L.shape, bool)
        for sy, sx in boxes(L.shape, reg.walls, erode=4):
            core[sy, sx] = True
        hp = L - cv2.GaussianBlur(L, (0, 0), GRAIN_SIGMA)
        out["grain"] = float(hp[core].std()) if core.any() else None

    # piel: la elipse achicada, de la nariz para arriba, y con color de piel (sin ojos, cejas ni pelo)
    skin = ellipses(L.shape, reg.faces, FACE_SHRINK) & upper_face(L.shape, reg.faces) & (C > 5) & (h > 20) & (h < 90) & (L > 25) & (L < 97)
    if skin.sum() > 200:
        Ls = L[skin]
        ma, mb = float(np.median(a[skin])), float(np.median(b[skin]))
        out["skin"] = {"p10": float(np.percentile(Ls, 10)), "p50": float(np.percentile(Ls, 50)),
                       "p90": float(np.percentile(Ls, 90)), "p98": float(np.percentile(Ls, 98)),
                       "a": ma, "b": mb, "C": float(np.hypot(ma, mb)), "h": hue(ma, mb), "n": int(skin.sum())}
        bands = []
        for lo, hi in SKIN_BANDS:
            m = skin & (L >= lo) & (L < hi)
            n = int(m.sum())
            if n >= MIN_BAND_PX:
                ba, bb = float(np.median(a[m])), float(np.median(b[m]))
                bands.append({"band": f"{lo}-{hi}", "n": n, "a": ba, "b": bb, "C": float(np.hypot(ba, bb)), "h": hue(ba, bb)})
            else:
                bands.append({"band": f"{lo}-{hi}", "n": n})
        out["bands"] = bands

    blk = boxes(L.shape, reg.blacks)
    if blk:
        vals = np.concatenate([L[s].ravel() for s in blk])
        out["black"] = {"p5": float(np.percentile(vals, 5)), "p50": float(np.percentile(vals, 50)),
                        "a": float(np.median(np.concatenate([a[s].ravel() for s in blk]))),
                        "b": float(np.median(np.concatenate([b[s].ravel() for s in blk])))}
    return out


def clip_percent(codes: np.ndarray) -> float:
    """% de pixeles con algun canal en el codigo maximo de su formato (65535 en 16 bits, 255 en 8)."""
    top = np.iinfo(codes.dtype).max
    hit = codes >= top
    return 100 * float(np.mean(hit.any(axis=-1) if codes.ndim == 3 else hit))


def read_master(name: str) -> np.ndarray:
    """La maestra tal cual esta en el archivo: sRGB de 16 bits. <foto>-antes es un PNG de 8 bits (grade.py)."""
    if name.endswith("-antes") and not (EDITED / f"{name}.tif").exists():
        return cv2.cvtColor(cv2.imread(str(EDITED / f"{name}.png"), cv2.IMREAD_UNCHANGED)[..., :3], cv2.COLOR_BGR2RGB)
    return tifffile.imread(EDITED / f"{name}.tif")


def read_reference_codes(ref: str) -> np.ndarray:
    """La referencia con sus codigos y su profundidad de archivo, sin el canal alfa."""
    codes = cv2.imread(str(ref_path(ref)), cv2.IMREAD_UNCHANGED)
    return codes[..., :3] if codes.ndim == 3 else codes


def at_scale(name: str, target_face_h: float, params: dict | None = None, srgb: np.ndarray | None = None) -> tuple[np.ndarray, Regions]:
    """La maestra (la entrega, ojeras al 70 %) achicada en luz lineal hasta que sus caras tengan el alto
    pedido (nunca agrandada), con los ajustes si los hay, y sus regiones a esa escala. `srgb`: la maestra ya
    leida con read_master, para no leerla dos veces."""
    if srgb is None:
        srgb = read_master(name)
    shape = srgb.shape[:2]
    reg = mine_regions(name, shape)
    lin = srgb_to_linear(srgb.astype(np.float32) / 65535)
    del srgb
    k = min(1.0, target_face_h / reg.face_height())
    if k < 1:
        lin = cv2.resize(lin, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
    if params:
        lin = adjust(lin, params)
    return lin, reg.scaled(lin.shape[1] / shape[1])


# --- la hoja ------------------------------------------------------------------------------------
def overlay(lin: np.ndarray, reg: Regions, height: int) -> Image.Image:
    k = height / lin.shape[0]
    small = cv2.resize(lin, (round(lin.shape[1] * k), height), interpolation=cv2.INTER_AREA)
    im = Image.fromarray(to_uint8(linear_to_srgb(small), dither=False))
    d = ImageDraw.Draw(im, "RGBA")
    for cx, cy, rx, ry in reg.faces:
        d.ellipse([(cx - rx * FACE_SHRINK) * k, (cy - ry * FACE_SHRINK) * k, (cx + rx * FACE_SHRINK) * k, (cy + ry * FACE_SHRINK) * k],
                  outline=(255, 210, 0, 220), width=2)
    for x0, y0, x1, y1 in reg.walls:
        d.rectangle([x0 * k, y0 * k, x1 * k, y1 * k], outline=(0, 220, 255, 220), width=2)
    for x0, y0, x1, y1 in reg.blacks:
        d.rectangle([x0 * k, y0 * k, x1 * k, y1 * k], outline=(255, 60, 160, 220), width=2)
    return im


def rows(m: dict) -> list[tuple[str, str]]:
    f = lambda v: "—" if v is None else f"{v:.1f}"  # noqa: E731
    out = [("Tono p1 p5 p50 p95 p99", " ".join(f"{v:.0f}" for v in m["tone"]))]
    if "wall" in m:
        w = m["wall"]
        out.append(("Pared L* a* b*", f"{w['L']:.1f}  {w['a']:+.1f}  {w['b']:+.1f}"))
        out.append(("Pared, de recuadro a recuadro", f"{w['spread']:.1f} ({' '.join(str(v) for v in w['each'])})"))
        out.append(("Grano (pared)", "—" if m.get("grain") is None else f"{m['grain']:.2f}"))
    if "skin" in m:
        s = m["skin"]
        out.append(("Piel sombra medio luz techo", f"{s['p10']:.0f}  {s['p50']:.0f}  {s['p90']:.0f}  {s['p98']:.0f}"))
        out.append(("Piel a* b* croma matiz", f"{s['a']:.1f}  {s['b']:.1f}  {s['C']:.1f}  {s['h']:.0f}°"))
        for band in m["bands"]:
            if "a" in band:
                out.append((f"  L* {band['band']}", f"C {band['C']:.1f}  {band['h']:.0f}°  (n {band['n']})"))
    if "black" in m:
        b = m["black"]
        out.append(("Negro p5 p50, a* b*", f"{b['p5']:.1f}  {b['p50']:.1f},  {b['a']:+.1f}  {b['b']:+.1f}"))
    if "clip" in m:
        out.append(("Recorte (clip %)", f"{m['clip']:.3f}"))
    return out


def sheet(ref: str, ref_img: Image.Image, ref_m: dict, mine: list[tuple[str, Image.Image, dict]], path: Path) -> None:
    font, bold = ImageFont.truetype(FONT, 17), ImageFont.truetype(FONT, 20, index=1)
    col_w = 330
    imgs = [(f"Referencia: {ref}", ref_img, ref_m)] + [(n, im, m) for n, im, m in mine]
    width = max(im.width for _, im, _ in imgs) + col_w * len(imgs) + 60
    height = (SHEET_H + 50) * len(imgs) + 20
    canvas = Image.new("RGB", (width, height), (24, 24, 26))
    d = ImageDraw.Draw(canvas)
    y = 10
    labels = [k for k, _ in rows(ref_m)]
    for title, im, m in imgs:
        d.text((20, y), title, fill=(240, 240, 240), font=bold)
        canvas.paste(im, (20, y + 34))
        x = 40 + max(i.width for _, i, _ in imgs)
        vals = dict(rows(m))
        for i, key in enumerate(labels):
            d.text((x, y + 40 + i * 26), key, fill=(170, 170, 175), font=font)
            d.text((x + 270, y + 40 + i * 26), vals.get(key, "—"), fill=(240, 240, 240), font=font)
        y += SHEET_H + 50
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def main(ref: str, names: list[str]) -> None:
    ref_lin, ref_reg = load_reference(ref), ref_regions(ref)
    ref_m = measure(ref_lin, ref_reg)
    ref_m["clip"] = clip_percent(read_reference_codes(ref))
    print(f"clip % {ref}: {ref_m['clip']:.3f}", flush=True)
    mine = []
    for name in names:
        srgb = read_master(name)
        clip = clip_percent(srgb)  # sobre el codigo maximo de su propio formato
        print(f"clip % {name}: {clip:.3f}", flush=True)
        if srgb.dtype == np.uint8:
            srgb = srgb.astype(np.uint16) * 257  # at_scale lee 16 bits
        lin, reg = at_scale(name, ref_reg.face_height(), srgb=srgb)
        del srgb
        m = measure(lin, reg)
        m["clip"] = clip
        mine.append((name, overlay(lin, reg, SHEET_H), m))
    out = PROCESS / f"estilos-medida-{ref}.png"
    sheet(ref, overlay(ref_lin, ref_reg, SHEET_H), ref_m, mine, out)
    notes = NOTES / "estilos" / f"medida-{ref}.json"
    notes.parent.mkdir(parents=True, exist_ok=True)
    notes.write_text(json.dumps({"ref": ref_m, **{n: m for n, _, m in mine}}, indent=1))
    print(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:] or PHOTO_NAMES)
