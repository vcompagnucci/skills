"""Prueba recipe/exacta.py: el tope de pendiente, la luz que se mueve sin llevarse la textura ni el color, el hombro, y
una foto real que se acerca a su referencia.

Uso: MallocLargeCache=0 nice -n 19 .venv/bin/python tools/exacta_check.py [foto estilo]
     sin foto y estilo, la primera foto con maestra de un estilo cuya referencia este en proceso/

- cap_slope: una T con pendiente ~10 dentro de la ventana queda con pendiente de a lo sumo 2,5, creciente, con su
  punto alto en el mismo lugar y de 0 a 100; sin tope, T tal cual.
- light_map, sobre una piel sintetica de L* 40 con un damero de +-2 y color (a* 15, b* 20): con T que lleva 40 a 60,
  la media llega a 60, el damero queda y a* y b* no se mueven.
- El pincel, en una cara sintetica: la piel de la cara y el cuello sube, la ropa negra de al lado no.
- shoulder_cut: nunca baja mas de lo que subio el relleno, y donde no subio nada no toca.
- La foto real, en la previa de 1024: la distancia media entre percentiles de piel y los de la referencia cae a menos
  de la mitad y a menos de 1,5 L*; a* y b* de la piel (la mediana, en la misma mascara) se mueven menos de 0,5.
- El archivo: escrito de una vez (sin temporales), con los permisos de una maestra, 16 bits y su perfil. Si la exacta
  de esa foto y estilo ya existe en editadas/, que tenga la medida de la maestra del estilo.
Escribe solo en work/exacta-check/ (que borra al final), proceso/exacta-<foto>-<estilo>.png y proceso-notas/exacta/.
"""

import os
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
import tifffile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "recipe"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import exacta  # noqa: E402
import ref_measure  # noqa: E402
from adjust import TO_LINEAR  # noqa: E402
from common import EDITED, ROOT, _srgb_icc, lab, lab_to_linear, to_uint16  # noqa: E402
from photos import PHOTOS  # noqa: E402
from references import ref_path  # noqa: E402

WORK = ROOT / "work" / "exacta-check"
failed = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'ok ' if ok else 'MAL'} {name}{'' if ok else f'  ({detail})'}", flush=True)
    if not ok:
        failed.append(name)


def check_cap() -> None:
    X = exacta.LIGHT_X
    T = np.interp(X, [0, 30, 40, 100], [0, 32, 132, 100])  # 30 -> 40 sube 100: pendiente 10
    T = np.maximum.accumulate(np.clip(T, 0, 100))
    window = (25.0, 70.0)
    out = exacta.cap_slope(T, exacta.SLOPE, window)
    i0, i1 = int(np.searchsorted(X, window[0])), int(np.searchsorted(X, window[1]))
    d = np.diff(out)[i0:i1]
    check("cap_slope: dentro de la ventana, pendiente de a lo sumo 2,5", bool(np.all(d <= exacta.SLOPE * np.diff(X)[i0:i1] + 1e-9)), f"max {float((d / np.diff(X)[i0:i1]).max()):.2f}")
    check("cap_slope: creciente, de 0 a 100, y el punto alto de la ventana donde estaba",
          bool(np.all(np.diff(out) >= -1e-12)) and out[0] == 0 and out[-1] == 100 and out[i1] == T[i1], f"{out[0]} {out[-1]} {out[i1]} {T[i1]}")
    check("cap_slope: con tope cambia T; sin tope la deja igual", not np.allclose(out, T) and exacta.cap_slope(T, None, window) is T)
    x, y = exacta.quantile_map([20, 30, 30.01, 50], [40, 45, 46, 70])
    check("quantile_map: de 0 a 100, creciente, y cada percentil a su par (sin los repetidos)",
          x[0] == 0 and x[-1] == 100 and y[0] == 0 and y[-1] == 100 and bool(np.all(np.diff(y) >= 0)) and list(x[1:-1]) == [20, 30, 50] and list(y[1:-1]) == [40, 45, 70],
          f"{x} {y}")


def check_light() -> None:
    h, w = 256, 256
    checker = ((np.indices((h, w)).sum(0) % 2) * 4 - 2).astype(np.float32)  # +-2 por pixel
    Lab = np.stack([40 + checker, np.full((h, w), 15, np.float32), np.full((h, w), 20, np.float32)], axis=-1)
    lin = lab_to_linear(Lab)
    ones = np.ones((h, w), np.float32)
    T = np.interp(exacta.LIGHT_X, [0, 40, 100], [0, 60, 100])
    out = lab(exacta.light_map(lin, ones > 0, ones, ones, T, sigma=8.0))
    L = out[..., 0]
    tex = float(np.abs(L - cv2.GaussianBlur(L, (0, 0), 3)).mean())
    tex0 = float(np.abs(Lab[..., 0] - cv2.GaussianBlur(Lab[..., 0], (0, 0), 3)).mean())
    check("light_map: la luz de la piel va de 40 a 60", abs(float(L.mean()) - 60) < 0.3, f"{L.mean():.2f}")
    check("light_map: el damero (la textura) queda", abs(tex / tex0 - 1) < 0.05, f"{tex:.3f} contra {tex0:.3f}")
    check("light_map: a* y b* no se mueven", float(np.abs(out[..., 1] - 15).max()) < 0.05 and float(np.abs(out[..., 2] - 20).max()) < 0.05,
          f"a* {out[..., 1].mean():.2f} b* {out[..., 2].mean():.2f}")
    zero = np.zeros((h, w), np.float32)
    same = exacta.light_map(lin, ones > 0, zero, ones, T, sigma=8.0)
    check("light_map: fuera del pincel no cambia nada", float(np.abs(same - lin).max()) < 1e-5)


def check_brush() -> None:
    """El pincel de una cara sintetica (piel de L* 50 arriba, ropa negra de L* 8 abajo): la piel sube, la ropa no."""
    h, w = 400, 300
    Lab = np.zeros((h, w, 3), np.float32)
    Lab[:250] = (50, 15, 20)
    Lab[250:] = (8, 0, 0)
    lin = lab_to_linear(Lab)
    alpha = np.ones((h, w), np.float32)
    skin, brush, r = exacta.skin_and_brush(lin, [(150, 140, 80, 100)], alpha)
    T = np.interp(exacta.LIGHT_X, [0, 50, 100], [0, 65, 100])
    out = lab(exacta.light_map(lin, skin, brush, alpha, T, exacta.LIGHT_SIGMA * r))
    check("pincel: la piel de la cara y el cuello sube", float(out[140, 150, 0]) > 60 and float(out[230, 150, 0]) > 60,
          f"{out[140, 150, 0]:.1f} {out[230, 150, 0]:.1f}")
    check("pincel: la ropa negra junto al cuello no se aclara", float(np.abs(out[252:, :, 0] - 8).max()) < 0.5, f"{float(np.abs(out[252:, :, 0] - 8).max()):.2f}")


def check_shoulder() -> None:
    rng = np.random.default_rng(0)
    L = (80 + 15 * rng.random((128, 128))).astype(np.float32)
    lifted = np.zeros_like(L)
    lifted[:, 64:] = 6.0
    cut = exacta.shoulder_cut(L, lifted, knee=80.0, ceiling=88.0, detail_sigma=0.0, alpha=np.ones_like(L))
    check("shoulder_cut: nunca baja mas de lo que subio el relleno", bool(np.all(cut <= lifted + 1e-6)), f"{float((cut - lifted).max()):.3f}")
    check("shoulder_cut: donde no subio nada no toca; donde subio, baja los brillos", float(cut[:, :64].max()) == 0 and float(cut[:, 64:].mean()) > 1,
          f"{float(cut[:, 64:].mean()):.2f}")


def pick() -> tuple[str, str] | None:
    import styles

    if len(sys.argv) == 3:
        return sys.argv[1], sys.argv[2]
    for photo in PHOTOS:
        for key, st in styles.STYLES.items():
            if (EDITED / f"{photo}-{key}.tif").exists() and ref_path(st["ref"]).exists():
                return photo, key
    return None


def check_photo() -> None:
    chosen = pick()
    if chosen is None:
        print("-- sin foto real: ninguna maestra de estilo tiene su referencia en proceso/ (tools/ref_import.py)")
        return
    photo, style = chosen
    exacta.PREVIEW = 1024
    rec = exacta.run(photo, style, exacta.SLOPE, n=1024, log=lambda *a, **k: None)
    hist = rec["preview"]["history"]
    d0, d1 = hist[0]["dq"], min(h["dq"] for h in hist[1:])
    check(f"{photo}-{style}: la piel se acerca a la referencia ({d0:.2f} -> {d1:.2f} L*)", d1 < d0 / 2 and d1 < 1.5, f"{d0:.2f} -> {d1:.2f}")
    # a* y b* en la misma mascara (la de la maestra), en la previa
    m16 = tifffile.imread(EDITED / f"{photo}-{style}.tif")
    H, W = m16.shape[:2]
    pre = cv2.cvtColor(cv2.imread(str(exacta.PROCESS / f"exacta-{photo}-{style}.png"), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGR2RGB)
    base = cv2.resize(TO_LINEAR[m16], (pre.shape[1], pre.shape[0]), interpolation=cv2.INTER_AREA)
    del m16
    got = lab(TO_LINEAR[pre.astype(np.uint16) * 257])
    want = lab(base)
    reg = ref_measure.mine_regions(f"{photo}-{style}", (H, W)).scaled(pre.shape[1] / W)
    m = ref_measure.skin_mask(want, reg)
    da = abs(float(np.median(got[..., 1][m]) - np.median(want[..., 1][m])))
    db = abs(float(np.median(got[..., 2][m]) - np.median(want[..., 2][m])))
    check(f"{photo}-{style}: a* y b* de la piel se mueven menos de 0,5", da < 0.5 and db < 0.5, f"a* {da:.2f} b* {db:.2f}")
    check(f"{photo}-{style}: la exacta no es la maestra", float(np.abs(got[..., 0] - want[..., 0])[m].mean()) > 0.5)
    tif = EDITED / f"{photo}-{style}-exacta.tif"
    if tif.exists():
        t = tifffile.imread(tif)
        check(f"{tif.name}: 16 bits, la medida de la maestra del estilo", t.dtype == np.uint16 and t.shape[:2] == (H, W), f"{t.dtype} {t.shape}")


def check_writer() -> None:
    shutil.rmtree(WORK, ignore_errors=True)
    WORK.mkdir(parents=True)
    path = WORK / "prueba-exacta.tif"
    img = np.linspace(0, 1, 64 * 48 * 3, dtype=np.float32).reshape(48, 64, 3)
    exacta.atomic(path, lambda p: tifffile.imwrite(p, to_uint16(img), compression="zlib", photometric="rgb", iccprofile=_srgb_icc()))
    mask = os.umask(0)
    os.umask(mask)
    with tifffile.TiffFile(path) as f:
        page = f.pages[0]
        icc = page.tags.get("InterColorProfile")
        data = page.asarray()
    check("el archivo: sin temporales, permisos de maestra, 16 bits y su perfil",
          [p.name for p in WORK.iterdir()] == [path.name] and (path.stat().st_mode & 0o777) == (0o666 & ~mask) and data.dtype == np.uint16 and icc is not None,
          f"{[p.name for p in WORK.iterdir()]} {oct(path.stat().st_mode & 0o777)}")
    shutil.rmtree(WORK, ignore_errors=True)


def main() -> int:
    check_cap()
    check_light()
    check_brush()
    check_shoulder()
    check_writer()
    check_photo()
    if failed:
        print(f"fallaron {len(failed)}: {', '.join(failed)}")
        return 1
    print("todo bien")
    return 0


if __name__ == "__main__":
    sys.exit(main())
