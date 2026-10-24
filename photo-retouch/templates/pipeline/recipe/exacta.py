"""Version exacta: la luz de la piel de un estilo igualada a la de su referencia, con tope de pendiente.

Uso: MallocLargeCache=0 nice -n 19 .venv/bin/python recipe/exacta.py <foto> [estilo ...] [--n 1536] [--tope 2.5 | --sin-tope]
     sin estilos, los de STYLES (recipe/styles.py) que tienen maestra; --n: solo la previa a ese lado largo, en
     proceso/exacta-<foto>-<estilo>.png, sin tocar editadas/

Las maestras de cada estilo no se tocan: esto escribe otras, editadas/<foto>-<estilo>-exacta.tif (16 bits) y .png
(8 bits), que el editor no lista. Lo medido va a proceso-notas/exacta/<foto>-<estilo>.json (la previa, a <foto>-<estilo>-previa.json).

Lo que iguala: los percentiles de L* de la piel (1 a 99, de a 2) a los de la referencia del estilo, medidos con el
mismo codigo y la misma mascara que tools/ref_measure.py (elipse de la cara achicada, de la nariz para arriba, con
color de piel), con la cara al alto de la de la referencia.
- La correccion es una transferencia T sobre la luz suave de la piel (el promedio de L* de la piel a LIGHT_SIGMA, en
  unidades de cara), que se suma en L* dentro de un pincel: la textura y el modelado chico quedan como en la maestra.
  T es la especificacion de histograma (Gonzalez y Woods) de mis percentiles a los de la referencia.
- Con tope de pendiente SLOPE (2,5 L* de salida por L* de luz) dentro de la luz que la piel tiene de verdad. Sin
  tope, una referencia con la piel pareja pide pendiente ~10 donde la piel de la foto tiene su quinto mas oscuro (el
  borde del pelo, la mandibula): esa piel se queda abajo, la de al lado sube 25 L* y quedan islas oscuras. El tope
  cambia exactitud por naturalidad, y lo que queda lejos se lee en el JSON.
- Un hombro en los brillos (shoulder_cut): con la luz subida, frente, nariz y pomulos llegaban a L* 96-100 donde la
  piel de la referencia termina en 89-91. Su techo se ajusta para que mi p99 de piel caiga en el de la referencia,
  y nunca baja mas de lo que subio el relleno.
- En color: se mueve solo L* (Lab), con a* y b* tal cual. El color de la gente es el de la maestra (la regla de
  STYLES: sin temperatura ni tinte en la gente); una ganancia en RGB lineal le cambiaba el a* y b* a la piel al subirla.
- El pincel: la piel de cada cara y su cuello (el ovalo agrandado y una franja hasta NECK radios abajo, con color de
  piel) con sus huecos cerrados (cejas, ojos), un cierre de r/1,5 y un borde de r/12 (r: el radio horizontal del
  ovalo), por el alpha de la persona: un relleno de luz ilumina toda esa zona, y en el borde se mueve solo la parte de
  persona del pixel. No entra a lo muy oscuro (DARK): la ropa negra y el pelo quedan como estan.

Se ajusta en una previa de 1536 px de lado largo (hasta ITERS vueltas o TOL_Q de error medio entre percentiles) y
despues se afina en la maestra entera (MASTER_ITERS vueltas), midiendo como ref_measure.py.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np
import tifffile
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import ref_measure  # noqa: E402
from adjust import TO_LINEAR  # noqa: E402
from common import EDITED, NOTES, PROCESS, _srgb_icc, lab, lab_to_linear, linear_to_srgb, save_png, to_uint8, to_uint16  # noqa: E402
from photos import PHOTOS  # noqa: E402
from references import load_reference, ref_path  # noqa: E402

QUANTILES = np.linspace(1, 99, 50)  # los puntos del histograma que se igualan (percentiles de L*)
LIGHT_X = np.linspace(0, 100, 401)  # la luz de la piel, en L*: donde se define T
LIGHT_SIGMA = 16 / 150  # la luz que se mueve, en radios de cara: lo de abajo es textura y modelado, y queda
SHOULDER_SIGMA = 1.5 / 150  # el hombro comprime la luz a esta escala: el poro y el brillo del ojo quedan
SLOPE = 2.5
KNEE_Q = 40  # la rodilla del hombro: el percentil 81 de la piel de la referencia (indice en QUANTILES)
TOL_Q = 0.6  # L*: diferencia media entre percentiles para dar el histograma por igual
ITERS = 8
MASTER_ITERS = 2
PREVIEW = 1536
OVAL_GROW = 1.15  # el pincel llega un poco mas alla del ovalo marcado: frente alta, mandibula y orejas
NECK = 2.0  # y baja hasta 2 radios verticales debajo del centro de la cara, en su ancho: el cuello
DARK = 12.0  # L*: desde aca hasta 10 mas arriba el pincel entra de a poco; abajo (ropa negra, pelo) no mueve nada
OUT_NOTES = NOTES / "exacta"


# --- la luz -------------------------------------------------------------------------------------
def skin_light(L: np.ndarray, skin: np.ndarray, sigma: float) -> np.ndarray:
    """El promedio de L* de la piel a `sigma`; donde no hay piel cerca, el de 4 sigma."""
    w = skin.astype(np.float32)
    den = cv2.GaussianBlur(w, (0, 0), sigma)
    low = cv2.GaussianBlur(L * w, (0, 0), sigma) / np.maximum(den, 1e-4)
    wide = cv2.GaussianBlur(L * w, (0, 0), 4 * sigma) / np.maximum(cv2.GaussianBlur(w, (0, 0), 4 * sigma), 1e-4)
    cover = np.clip(den / 0.15, 0, 1)
    return cover * low + (1 - cover) * wide


def quantile_map(have_q: np.ndarray, want_q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(x, y) de la correccion que lleva mis percentiles a los de la referencia; se apaga hasta 0 y 100."""
    h, w = np.asarray(have_q, np.float64), np.asarray(want_q, np.float64)
    keep = np.concatenate([[True], np.diff(h) > 0.05])
    h, w = h[keep], np.maximum.accumulate(w[keep])
    return np.concatenate([[0.0], h, [100.0]]), np.maximum.accumulate(np.concatenate([[0.0], w, [100.0]]))


def cap_slope(T: np.ndarray, slope: float | None, window: tuple[float, float]) -> np.ndarray:
    """T con pendiente de a lo sumo `slope` dentro de `window` (la luz que la piel tiene de verdad); T(hi) queda donde
    esta y lo que falta se suma como un levante parejo abajo. Fuera de la ventana no hay piel: ahi la rampa desde 0
    puede ser empinada, y es la que deja levantar pareja toda la cara."""
    if slope is None:
        return T
    lo, hi = window
    i0, i1 = int(np.searchsorted(LIGHT_X, lo)), int(np.searchsorted(LIGHT_X, hi))
    d = np.diff(T)
    capped = np.clip(d[i0:i1], 0, slope * np.diff(LIGHT_X)[i0:i1])
    out = T.copy()
    out[i0:i1 + 1] = T[i1] - np.concatenate([np.cumsum(capped[::-1])[::-1], [0.0]])
    if i0 > 0 and T[i0] > 0:  # la rampa desde 0, estirada hasta el nuevo comienzo de la ventana
        out[:i0] = T[:i0] * out[i0] / T[i0]
    return np.maximum.accumulate(np.clip(out, 0, 100))


def shoulder_cut(L: np.ndarray, lifted: np.ndarray, knee: float, ceiling: float, detail_sigma: float,
                 alpha: np.ndarray) -> np.ndarray:
    """Cuanto bajar cada pixel para que sus brillos vayan hacia `ceiling` desde `knee` (pendiente 1 en la rodilla).
    - Se comprime la luz a `detail_sigma` px, no el pixel: el brillo del ojo y el poro quedan arriba.
    - Nunca baja mas de lo que subio el relleno (`lifted`): donde no se subio luz no toca nada, y un pixel del borde a
      lo sumo vuelve al de la maestra.
    - En el borde de la persona (alpha < 1 y unos px adentro) se comprime el pixel: ahi la luz promediada mezcla la
      pared, queda abajo de la rodilla, y el filo de piel iluminada del contorno salia como una linea blanca."""
    base = cv2.GaussianBlur(L, (0, 0), detail_sigma) if detail_sigma > 0 else L
    if detail_sigma > 0:
        edge = cv2.GaussianBlur((alpha < 0.99).astype(np.float32), (0, 0), detail_sigma)
        np.clip(edge * 4, 0, 1, out=edge)
        base = base + np.maximum(L - base, 0) * edge
        del edge
    span = ceiling - knee
    over = np.maximum(base - knee, 0)
    cut = over - span * (1 - np.exp(-over / span))
    return np.minimum(cut, lifted)


def light_map(lin: np.ndarray, skin: np.ndarray, brush: np.ndarray, alpha: np.ndarray, T: np.ndarray, sigma: float,
              knee: float = 100.0, ceiling: float = 100.0, detail_sigma: float = 0.0) -> np.ndarray:
    """La luz suave de la piel llevada por T, sumada en L* dentro del pincel; a* y b* quedan. Luz lineal (h, w, 3)."""
    if np.allclose(T, LIGHT_X) and ceiling >= 100:
        return lin
    Lab = lab(lin)
    L = Lab[..., 0]
    low = skin_light(L, skin, sigma)
    shift = np.interp(low, LIGHT_X, T).astype(np.float32)
    shift -= low
    del low
    shift *= brush
    L += shift
    if ceiling < 100:
        L -= shoulder_cut(L, np.maximum(shift, 0), knee, ceiling, detail_sigma, alpha)
    del shift
    np.clip(L, 0, 100, out=L)
    return np.clip(lab_to_linear(Lab), 0, 1)


# --- la piel, medida como ref_measure.py ---------------------------------------------------------
def quantiles(lin: np.ndarray, reg: "ref_measure.Regions") -> np.ndarray:
    Lab = lab(lin)
    m = ref_measure.skin_mask(Lab, reg)
    if m.sum() <= 200:
        raise SystemExit("muy poca piel medible en la cara marcada")
    return np.percentile(Lab[..., 0][m], QUANTILES)


def skin_and_brush(lin: np.ndarray, faces: list, alpha: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """La piel (para promediar la luz) y el pincel (donde se suma), con los ovalos en px de `lin`; y el radio medio."""
    Lab = lab(lin)
    C = np.hypot(Lab[..., 1], Lab[..., 2])
    h = np.degrees(np.arctan2(Lab[..., 2], Lab[..., 1])) % 360
    color = (C > 5) & (h > 20) & (h < 90) & (Lab[..., 0] > 25) & (Lab[..., 0] < 97)
    del Lab, C, h
    zone = ref_measure.ellipses(lin.shape[:2], faces, OVAL_GROW)
    for cx, cy, rx, ry in faces:  # el cuello: sin el, la luz de la cara cortaba en la mandibula
        zone[max(0, round(cy)):round(cy + NECK * ry), max(0, round(cx - rx)):round(cx + rx)] = True
    skin = zone & color & (alpha > 0.5)
    r = float(np.mean([f[2] for f in faces]))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(r / 1.5) | 1,) * 2)
    closed = cv2.morphologyEx(skin.astype(np.uint8), cv2.MORPH_CLOSE, k).astype(np.float32)
    brush = cv2.GaussianBlur(closed, (0, 0), r / 12) * alpha
    # el borde del pincel no entra a lo oscuro (la ropa negra junto al cuello, el pelo): ahi el desenfoque sumaba la
    # luz de la piel y dejaba un halo claro en el cuello de la remera
    brush *= np.clip((lab(lin)[..., 0] - DARK) / 10, 0, 1)
    return skin, brush.astype(np.float32), r


def alpha_of(photo: str, shape: tuple[int, int]) -> np.ndarray:
    """El alpha de la persona (el del fondo de styles.py), al tamano pedido."""
    import styles  # aca: styles carga el matting

    layers = styles.layers_for(photo, styles.master(photo))
    a = layers.alpha16
    if a.shape[:2] != shape:
        a = cv2.resize(a.astype(np.float32), (shape[1], shape[0]), interpolation=cv2.INTER_AREA)
    return (np.asarray(a, np.float32) / 65535).astype(np.float32)


# --- el ajuste ----------------------------------------------------------------------------------
def fit(lin: np.ndarray, faces: list, alpha: np.ndarray, measure_at, want_q: np.ndarray, slope: float | None,
        iters: int, T: np.ndarray | None = None, ceiling: float = 100.0, log=print) -> dict:
    """Igualar los percentiles de la piel de `lin` a want_q. measure_at(img) devuelve mis percentiles medidos como
    ref_measure. Devuelve T, el techo, la imagen y la historia."""
    skin, brush, r = skin_and_brush(lin, faces, alpha)
    sigma, detail = LIGHT_SIGMA * r, SHOULDER_SIGMA * r
    low0 = skin_light(lab(lin)[..., 0], skin, sigma)
    window = tuple(float(v) for v in np.percentile(low0[brush > 0.5], [0.5, 99.5]))
    del low0
    T = np.array(LIGHT_X if T is None else T, np.float64)
    knee = float(want_q[KNEE_Q])
    history, out = [], lin
    q0 = measure_at(lin)
    history.append({"it": -1, "dq": float(np.abs(q0 - want_q).mean()), "q": q0.tolist()})
    for it in range(iters):
        out = light_map(lin, skin, brush, alpha, T, sigma, knee, ceiling, detail)
        q = measure_at(out)
        dq = float(np.abs(q - want_q).mean())
        history.append({"it": it, "dq": dq, "q": q.tolist(), "ceiling": ceiling, "T": T[::8].tolist()})
        log(f"  vuelta {it}: piel a {dq:.2f} L* de la referencia (p99 {q[-1]:.1f} contra {want_q[-1]:.1f}), techo {ceiling:.1f}", flush=True)
        if dq < TOL_Q or it == iters - 1:
            break
        T = cap_slope(np.interp(T, *quantile_map(q, want_q)), slope, window)
        top, want_top = float(q[-1]), float(want_q[-1])
        if top > want_top + 0.3 or ceiling < 100:
            ceiling = float(np.clip(knee + (ceiling - knee) * (want_top - knee) / max(top - knee, 0.5), knee + 1, 100))
    return {"T": T, "ceiling": ceiling, "image": out, "history": history, "window": window, "knee": knee}


def atomic(path: Path, write) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.stem}-", suffix=path.suffix)
    os.close(fd)
    try:
        write(Path(tmp))
        mask = os.umask(0)
        os.umask(mask)
        os.chmod(tmp, 0o666 & ~mask)  # mkstemp lo crea 600: que quede como las otras maestras
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)


def run(photo: str, style: str, slope: float | None = SLOPE, n: int | None = None, log=print) -> dict:
    """Ajusta y escribe la exacta de photo × style. Con n, solo la previa (en proceso/) y lo medido."""
    import styles

    ref = styles.STYLES[style]["ref"]
    if not ref_path(ref).exists():
        raise SystemExit(f"falta {ref_path(ref).relative_to(PROCESS.parent)}: importarla con tools/ref_import.py")
    ref_lin, ref_reg = load_reference(ref), ref_measure.ref_regions(ref)
    want_q = quantiles(ref_lin, ref_reg)
    face_h = ref_reg.face_height()
    del ref_lin
    key = f"{photo}-{style}"
    m16 = tifffile.imread(EDITED / f"{key}.tif")
    H, W = m16.shape[:2]
    faces = [f["oval"][:4] for f in PHOTOS[photo]["faces"]]

    def measure_at(img: np.ndarray) -> np.ndarray:
        """Mis percentiles como ref_measure: la cara al alto de la de la referencia (nunca agrandada)."""
        k = img.shape[1] / W
        reg = ref_measure.mine_regions(key, (H, W)).scaled(k)
        s = min(1.0, face_h / reg.face_height())
        if s < 1:
            img = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
            reg = reg.scaled(s)
        return quantiles(img, reg)

    log(f"{key} (referencia {ref}, tope {slope if slope is not None else 'ninguno'}):", flush=True)
    k = min(1.0, PREVIEW / max(H, W))
    small = cv2.resize(TO_LINEAR[m16], (round(W * k), round(H * k)), interpolation=cv2.INTER_AREA)
    alpha_full = alpha_of(photo, (H, W))
    a_small = cv2.resize(alpha_full, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_AREA)
    pre = fit(small, [tuple(v * k for v in f) for f in faces], a_small, measure_at, want_q, slope, ITERS, log=log)
    record = {"photo": photo, "style": style, "reference": ref, "slope": slope, "want": want_q.tolist(),
              "window": pre["window"], "knee": pre["knee"], "preview": {"side": PREVIEW, "history": pre["history"]}}
    OUT_NOTES.mkdir(parents=True, exist_ok=True)
    if n is not None:
        save_png(linear_to_srgb(pre["image"]), PROCESS / f"exacta-{key}.png")
    else:
        del small, a_small
        lin = TO_LINEAR[m16]
        del m16
        full = fit(lin, faces, alpha_full, measure_at, want_q, slope, MASTER_ITERS, T=pre["T"], ceiling=pre["ceiling"], log=log)
        del lin
        record["master"] = {"history": full["history"], "ceiling": full["ceiling"], "T": full["T"][::8].tolist()}
        srgb = linear_to_srgb(full.pop("image"))
        tif, png = EDITED / f"{key}-exacta.tif", EDITED / f"{key}-exacta.png"
        atomic(tif, lambda p: tifffile.imwrite(p, to_uint16(srgb), compression="zlib", photometric="rgb", iccprofile=_srgb_icc()))
        atomic(png, lambda p: Image.fromarray(to_uint8(srgb)).save(p, format="PNG", icc_profile=_srgb_icc(), compress_level=6))
        del srgb
        log(f"{key}-exacta: escrita", flush=True)
    # la previa va aparte: una prueba (tools/exacta_check.py) no pisa lo medido de la maestra
    (OUT_NOTES / f"{key}{'-previa' if n is not None else ''}.json").write_text(json.dumps(record, indent=1))
    return record


def main(args: list[str]) -> None:
    import styles

    slope, n, rest = SLOPE, None, []
    i = 0
    while i < len(args):
        if args[i] == "--tope":
            slope, i = float(args[i + 1]), i + 2
        elif args[i] == "--sin-tope":
            slope, i = None, i + 1
        elif args[i] == "--n":
            n, i = int(args[i + 1]), i + 2
        else:
            rest.append(args[i])
            i += 1
    if not rest or rest[0] not in PHOTOS:
        raise SystemExit(__doc__.split("\n\n")[1])
    photo, keys = rest[0], rest[1:] or [s for s in styles.STYLES if (EDITED / f"{rest[0]}-{s}.tif").exists()]
    global PREVIEW
    if n is not None:
        PREVIEW = n
    for key in keys:
        if key not in styles.STYLES:
            raise SystemExit(f"{key}: no es un estilo de STYLES")
        run(photo, key, slope, n)


if __name__ == "__main__":
    main(sys.argv[1:])
