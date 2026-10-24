"""Los ajustes equivalentes de cada foto: los valores del panel con los que arranca el editor.

Uso: MallocLargeCache=0 nice -n 19 .venv/bin/python recipe/equivalents.py [foto ...]

La maestra (editadas/<foto>.tif, la de grade.py) no se hizo con los controles del panel: son curvas medidas, luz
local y grano, asi que no tiene "sus" valores. Aca se buscan los que mas se le parecen: los parametros de adjust.py
(la misma funcion del servidor y del shader) con los que adjust(RAW original) queda mas cerca de la maestra. Las dos
imagenes estan alineadas pixel a pixel (el antes y despues del editor depende de eso).

- A 1024 px de lado largo, las dos achicadas igual (en luz lineal, INTER_AREA, como resample() del servidor).
- Los once controles de Light y Color; la diferencia es la de Lab (Delta E 1976).
- scipy.optimize.least_squares con los limites del panel (exposicion +-2, el resto +-100), perdida soft_l1, sobre una
  grilla de 1 de cada 4 pixeles por lado, desde dos arranques. Despues se redondea al paso de cada control (0,01 la
  exposicion, 1 el resto), se pule de a un paso y el residuo se mide en la imagen entera de 1024.

En el editor la maestra se ve tal cual, y estos valores son solo el punto de partida del panel: mover un control
aplica la diferencia con el punto de partida sobre la maestra (el servidor recibe esa diferencia, nunca el punto de
partida). Las versiones guardan los valores del panel, absolutos.

Escribe recipe/equivalents.json (lo lee viewer.py para el editor), proceso-notas/equivalentes/equivalentes.txt y la
hoja proceso/equivalentes-hoja.png. Una foto cuya maestra y RAW no cambiaron (su firma) no se vuelve a ajustar.

Las versiones (editadas/versiones.json): las que se guardaron antes de que la foto tuviera punto de partida son
diferencias sobre la maestra (el punto de partida era 0). La primera vez que una foto entra a equivalents.json, a
Light y Color de cada version de esa foto (y de lo que estaba abierto) se les suma su punto de partida, asi se siguen
viendo igual; antes se copia versiones.json a respaldos/. Cuando el punto de partida se vuelve a calcular (cambio la
maestra), las versiones no se tocan: son valores absolutos, y cada una pasa a aplicar otra diferencia; se listan para
revisarlas. Con el editor abierto, recargar la pagina despues: una pagina abierta antes guarda sin el punto de partida.
"""

import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

import cv2
import numpy as np
import tifffile
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adjust  # noqa: E402
from common import EDITED, NOTES, PROCESS, ROOT, lab, linear_to_srgb, to_uint8  # noqa: E402
from photos import PHOTOS  # noqa: E402

STARTS = ROOT / "recipe" / "equivalents.json"
VERSIONS = EDITED / "versiones.json"
BACKUPS = ROOT / "respaldos"
SIDE = 1024  # lado largo
GRID = 4  # el ajuste mira 1 de cada 4 pixeles por lado; el residuo, todos
ROUGH = 3.0  # media de |Delta L*| desde la que el equivalente es solo aproximado
# de cada ajuste, su control en el panel, plano como lo guarda DialKit ("Light.Exposure")
UI = {"exposure": "Light.Exposure", "brightness": "Light.Brightness", "contrast": "Light.Contrast",
      "highlights": "Light.Highlights", "shadows": "Light.Shadows", "whites": "Light.Whites", "blacks": "Light.Blacks",
      "temperature": "Color.Temperature", "tint": "Color.Tint", "vibrance": "Color.Vibrance", "saturation": "Color.Saturation"}


def load_starts() -> dict[str, dict[str, float]]:
    """Los puntos de partida, {foto: {ajuste: valor}}. Sin el archivo, ninguno (el panel arranca en 0)."""
    try:
        data = json.loads(STARTS.read_text())
    except FileNotFoundError:
        return {}
    return {k: v["values"] for k, v in data.get("photos", {}).items()}


def step(key: str, v: float) -> float:
    """Al paso del control: 0,01 la exposicion, 1 el resto."""
    return round(v, 2) if key == "exposure" else float(round(v))


def shifted(flat: dict, delta: dict[str, float]) -> dict:
    """Unos valores planos de DialKit con delta sumado a Light y Color. Un control que no esta no se agrega: el editor
    lo completa con el punto de partida (diferencia 0), lo mismo que antes valia 0."""
    out = dict(flat)
    for k, name in UI.items():
        if isinstance(out.get(name), (int, float)) and not isinstance(out[name], bool) and delta.get(k):
            out[name] = step(k, out[name] + delta[k])
    return out


def shift_versions(photos: dict[str, dict[str, float]]) -> list[str]:
    """Suma a cada version de esas fotos su punto de partida (lo que estaba abierto incluido). Respaldo antes."""
    if not photos or not VERSIONS.exists():
        return []
    data = json.loads(VERSIONS.read_text())
    touched = [k for k in photos if k in data.get("photos", {})]
    if not touched:
        return []
    BACKUPS.mkdir(exist_ok=True)
    shutil.copy2(VERSIONS, BACKUPS / f"versiones-antes-equivalentes-{time.strftime('%Y%m%d-%H%M%S')}.json")
    for k in touched:
        st, d = data["photos"][k], photos[k]
        st["values"], st["baseValues"] = shifted(st["values"], d), shifted(st["baseValues"], d)
        for p in st["presets"]:
            p["values"] = shifted(p["values"], d)
    fd, tmp = tempfile.mkstemp(dir=EDITED, prefix=".versiones-", suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, VERSIONS)
    return touched


def to_side(lin: np.ndarray) -> np.ndarray:
    h, w = lin.shape[:2]
    k = SIDE / max(h, w)
    return cv2.resize(lin, (max(1, round(w * k)), max(1, round(h * k))), interpolation=cv2.INTER_AREA)


def load(photo: str) -> tuple[np.ndarray, np.ndarray]:
    """El RAW original (8 bits llevados a 16) y la maestra de 16 bits, en luz lineal y a 1024 px."""
    raw8 = cv2.imread(str(EDITED / f"{photo}-antes.png"), cv2.IMREAD_UNCHANGED)
    master = tifffile.imread(EDITED / f"{photo}.tif")
    if raw8 is None or raw8.shape[:2] != master.shape[:2]:
        raise ValueError(f"{photo}: el RAW original y la maestra no tienen la misma medida")
    raw = to_side(adjust.TO_LINEAR[cv2.cvtColor(raw8, cv2.COLOR_BGR2RGB).astype(np.uint16) * 257])
    del raw8
    lin = to_side(adjust.TO_LINEAR[master])
    del master
    return raw, lin


def signature(photo: str) -> dict:
    sig = lambda p: [p.stat().st_mtime_ns, p.stat().st_size]
    return {"raw": sig(EDITED / f"{photo}-antes.png"), "master": sig(EDITED / f"{photo}.tif")}


def params_of(x: np.ndarray) -> dict:
    """Del vector del ajuste (exposicion en pasos, el resto en -1..1) a los valores del panel."""
    return {k: float(v) * (1 if k == "exposure" else 100) for k, v in zip(adjust.KEYS, x)}


def rounded(p: dict) -> dict:
    return {k: step(k, v) for k, v in p.items()}


def difference(src: np.ndarray, target_lab: np.ndarray, p: dict) -> np.ndarray:
    return lab(adjust.adjust(src, p)) - target_lab


def residual(src: np.ndarray, target_lab: np.ndarray, p: dict) -> dict:
    d = difference(src, target_lab, p)
    dl, de = np.abs(d[..., 0]), np.linalg.norm(d, axis=-1)
    return {"mean_dL": float(dl.mean()), "p95_dL": float(np.percentile(dl, 95)),
            "mean_dE": float(de.mean()), "p95_dE": float(np.percentile(de, 95))}


def score(src: np.ndarray, target_lab: np.ndarray, p: dict) -> float:
    """Lo mismo que minimiza least_squares (soft_l1, f_scale 1), para comparar candidatos ya redondeados."""
    d = difference(src, target_lab, p)
    return float((2 * (np.sqrt(1 + d * d) - 1)).sum())


def fit(raw: np.ndarray, master: np.ndarray) -> tuple[dict, dict, list]:
    from scipy.optimize import least_squares  # aca: importar este modulo (viewer.py, styles.py) no carga scipy

    target = lab(master)
    src, tgt = raw[::GRID, ::GRID].reshape(-1, 3), target[::GRID, ::GRID].reshape(-1, 3)
    lo = np.array([-adjust.EXPOSURE if k == "exposure" else -1.0 for k in adjust.KEYS])
    hi = -lo

    def f(x):
        return difference(src, tgt, params_of(x)).ravel()

    y = lambda img: float((img @ adjust.LUMA).mean())
    seeds = [np.zeros(len(adjust.KEYS)), np.zeros(len(adjust.KEYS))]
    seeds[1][0] = np.clip(np.log2(y(master) / max(y(raw), 1e-6)), lo[0] + 0.01, hi[0] - 0.01)  # la luz media, igualada
    best = None
    for x0 in seeds:
        r = least_squares(f, x0, bounds=(lo, hi), loss="soft_l1", f_scale=1.0, diff_step=1e-3, x_scale=0.3, max_nfev=400)
        if best is None or r.cost < best.cost:
            best = r
    p = rounded(params_of(best.x))
    # el redondeo al paso de cada control, pulido de a un paso mientras mejore
    cur = score(src, tgt, p)
    for _ in range(6):
        moved = False
        for k in adjust.KEYS:
            unit = 0.01 if k == "exposure" else 1.0
            limit = adjust.EXPOSURE if k == "exposure" else 100
            for s in (unit, -unit):
                q = dict(p, **{k: step(k, p[k] + s)})
                if abs(q[k]) > limit:
                    continue
                c = score(src, tgt, q)
                if c < cur:
                    p, cur, moved = q, c, True
                    break
        if not moved:
            break
    edges = [k for k in adjust.KEYS if abs(p[k]) >= (adjust.EXPOSURE if k == "exposure" else 100)]
    return p, residual(raw, target, p), edges


def describe(p: dict) -> str:
    return "  ".join(f"{k[:4].capitalize()} {p[k]:+.2f}" if k == "exposure" else f"{k[:4].capitalize()} {p[k]:+.0f}" for k in adjust.KEYS)


def tile(lin: np.ndarray, h: int) -> np.ndarray:
    k = h / lin.shape[0]
    small = cv2.resize(lin, (max(1, round(lin.shape[1] * k)), h), interpolation=cv2.INTER_AREA)
    return to_uint8(linear_to_srgb(np.clip(small, 0, 1)), dither=False)


def sheet(rows: list, path: Path, h: int = 480) -> None:
    gap, head = 16, 92
    widths = [sum(t.shape[1] for t in tiles) + gap * (len(tiles) + 1) for _, _, tiles in rows]
    canvas = Image.new("RGB", (max(widths), len(rows) * (h + head + gap) + gap), (12, 12, 12))
    draw = ImageDraw.Draw(canvas)
    big = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    y = gap
    for title, line, tiles in rows:
        draw.text((gap, y), title, fill=(235, 235, 235), font=big)
        draw.text((gap, y + 34), line, fill=(170, 170, 170), font=small)
        draw.text((gap, y + 60), "RAW original   |   RAW + equivalent sliders   |   Master", fill=(120, 120, 120), font=small)
        x = gap
        for t in tiles:
            canvas.paste(Image.fromarray(t), (x, y + head))
            x += t.shape[1] + gap
        y += h + head + gap
    canvas.save(path)


def main(args: list[str]) -> None:
    names = [n for n in PHOTOS if (EDITED / f"{n}.tif").exists() and (EDITED / f"{n}-antes.png").exists()]
    only = set(args) or set(names)
    if only - set(names):
        raise SystemExit(f"sin maestra o sin RAW original: {', '.join(sorted(only - set(names)))}")
    try:
        data = json.loads(STARTS.read_text())
    except FileNotFoundError:
        data = {"photos": {}}
    new, moved, rows = {}, {}, []
    for photo in names:
        sig = signature(photo)
        done = data["photos"].get(photo)
        redo = done is None or (photo in only and done.get("sig") != sig)  # lo que falta se ajusta siempre
        raw, master = load(photo)
        if redo:
            t = time.time()
            values, res, edges = fit(raw, master)
            if done is None:
                new[photo] = values
            elif done["values"] != values:
                moved[photo] = (done["values"], values)
            data["photos"][photo] = {"values": values, "residual": res, "at_limit": edges, "sig": sig}
            print(f"{photo}: {time.time() - t:.0f} s  |dL*| {res['mean_dL']:.2f}  dE76 {res['mean_dE']:.2f}  {describe(values)}", flush=True)
        done = data["photos"][photo]
        res = done["residual"]
        line = f"mean |dL*| {res['mean_dL']:.2f}  p95 {res['p95_dL']:.2f}   mean dE76 {res['mean_dE']:.2f}  p95 {res['p95_dE']:.2f}"
        if res["mean_dL"] > ROUGH or done["at_limit"]:
            line += "   ROUGH EQUIVALENT"
        rows.append((f"{photo}   {describe(done['values'])}", line, [tile(raw, 480), tile(adjust.adjust(raw, done["values"]), 480), tile(master, 480)]))
        del raw, master
    # primero las versiones (con respaldo), despues el archivo: si algo falla en el medio, la proxima pasada las vuelve
    # a encontrar sin punto de partida y las mueve una sola vez
    touched = shift_versions(new)
    fd, tmp = tempfile.mkstemp(dir=STARTS.parent, prefix=".equivalents-", suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f, indent=1)
        f.write("\n")
    os.replace(tmp, STARTS)
    PROCESS.mkdir(exist_ok=True)
    sheet(rows, PROCESS / "equivalentes-hoja.png")
    out = NOTES / "equivalentes"
    out.mkdir(parents=True, exist_ok=True)
    lines = ["foto      " + "  ".join(f"{k:>11}" for k in adjust.KEYS) + "   |dL*| media  p95   dE76 media  p95"]
    for photo in names:
        d = data["photos"][photo]
        v, r = d["values"], d["residual"]
        cells = "  ".join(f"{v[k]:>11.2f}" if k == "exposure" else f"{v[k]:>11.0f}" for k in adjust.KEYS)
        flag = "  APROXIMADO" if r["mean_dL"] > ROUGH or d["at_limit"] else ""
        limit = f"  (en el limite: {', '.join(d['at_limit'])})" if d["at_limit"] else ""
        lines.append(f"{photo}  {cells}   {r['mean_dL']:>10.2f}  {r['p95_dL']:.2f}   {r['mean_dE']:>10.2f}  {r['p95_dE']:.2f}{flag}{limit}")
    (out / "equivalentes.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if touched:
        print(f"versiones con el punto de partida sumado (respaldo en respaldos/): {', '.join(touched)}. Con el editor abierto, recargar la pagina")
    for photo, (a, b) in moved.items():
        print(f"{photo}: el punto de partida cambio ({describe(a)} -> {describe(b)}); sus versiones no se tocan, revisarlas")


if __name__ == "__main__":
    main(sys.argv[1:])
