"""Prueba del servidor del editor: exportar con luz y color y con el fondo, el DNG, Flip, la forma (circulo), nombres de archivo y versiones guardadas.

Uso: .venv/bin/python tools/editor_test/test_server.py

Arranca recipe/editor_server.py en el puerto 8791 y lo apaga siempre al final. editadas/versiones.json
se respalda antes y se deja como estaba.
"""

import http.client
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import cv2
import numpy as np
import tifffile

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "recipe"))
import adjust  # noqa: E402
import backdrop  # noqa: E402
import editor_server  # noqa: E402  (importarlo no arranca nada)
from photos import PHOTOS, STUDIO  # noqa: E402

PORT = 8791
HOST = f"127.0.0.1:{PORT}"
VERSIONS = ROOT / "editadas" / "versiones.json"
# la foto de la prueba: EDITOR_TEST_PHOTO, o la primera de la sesion (recipe/photos.py). Tiene que tener pared (para
# el fondo) y al menos una cara inventariada (para las ojeras)
PHOTO = os.environ.get("EDITOR_TEST_PHOTO") or STUDIO[0]
OTHER = next((k for k in STUDIO if k != PHOTO), None)  # una segunda foto, para las versiones de dos fotos
_cx, _cy = PHOTOS[PHOTO]["faces"][0]["oval"][:2]
_H, _W = tifffile.TiffFile(ROOT / "editadas" / f"{PHOTO}.tif").pages[0].shape[:2]  # la maestra
# toca el parche de ojeras de la primera cara, sin salirse de la foto
BOX = [min(max(int(_cx) - 512, 0), max(_W - 1024, 0)), min(max(int(_cy) - 512, 0), max(_H - 1024, 0)), 1024, 1024]
ALL_ON = {k: (0.6 if k == "exposure" else 35 - 7 * i) for i, k in enumerate(adjust.KEYS)}
BG_ON = {"exposure": 0.45, "evenness": 65, "falloff": 30, "temperature": 40, "tint": -12, "saturation": -100}

failed = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'ok ' if ok else 'MAL'} {name}{'' if ok else f'  ({detail})'}", flush=True)
    if not ok:
        failed.append(name)


def call(method: str, path: str, body=None, headers=None, raw: bytes | None = None) -> tuple[int, dict, bytes]:
    conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=30)
    h = {"Host": HOST}
    if body is not None or raw is not None:
        h["Content-Type"] = "application/json"
    h.update(headers or {})
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    try:
        conn.request(method, path, body=data, headers=h)
        r = conn.getresponse()
        return r.status, dict(r.getheaders()), r.read()
    finally:
        conn.close()


def prepare(**extra) -> tuple[int, dict]:
    req = {"photo": PHOTO, "image": "edit", "box": BOX, "size": "full", "format": "png"} | extra
    status, _, data = call("POST", "/api/prepare", req)
    return status, json.loads(data)


def download(fid: str) -> bytes:
    status, _, data = call("GET", f"/api/file/{fid}")
    assert status == 200, status
    return data


def decode(png: bytes) -> np.ndarray:
    img = cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_UNCHANGED)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def state(n: int = 1, active: str | None = "preset-a") -> dict:
    presets = [{"id": f"preset-{'a' if i == 0 else i}", "name": f"Version {i + 1}", "values": {"Light.exposure": 0.3 * i}}
               for i in range(n)]
    return {"version": 1, "values": {"Light.exposure": 0.5, "Color.tint": -12, "Panel.open": True, "mode": "edit"},
            "baseValues": {"Light.exposure": 0}, "presets": presets, "activePresetId": active}


def wait_ready(proc: subprocess.Popen) -> None:
    for _ in range(150):
        if proc.poll() is not None:
            raise RuntimeError("el servidor se cerro al arrancar")
        try:
            if call("GET", "/editor.html")[0] == 200:
                return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("el servidor no contesto")


def test_prepare() -> None:
    x, y, w, h = BOX
    full = tifffile.imread(ROOT / "editadas" / f"{PHOTO}.tif")
    crop = full[y : y + h, x : x + w].copy()
    del full
    manifest = editor_server.eye_manifest()[0]
    default = manifest["intensity"]
    suffix = f"-crop-{w}x{h}.png"

    s1, r1 = prepare()
    a = download(r1["id"])
    s2, r2 = prepare(adjust={k: 0 for k in adjust.KEYS})
    b = download(r2["id"])
    check("neutro: identico con y sin adjust en 0", s1 == s2 == 200 and a == b)
    check("neutro: los pixeles de la maestra", np.array_equal(decode(a), crop))
    check("nombre neutro", r1["name"] == f"{PHOTO}{suffix}" and r1["adjusted"] is False and r1["version"] is None, r1["name"])

    s, r = prepare(adjust=ALL_ON)
    got = decode(download(r["id"])).astype(np.int32)
    want = adjust.adjust_uint16(editor_server.blend_eyes(crop, PHOTO, x, y, default, manifest), adjust.parse(ALL_ON))
    diff = int(np.abs(got - want).max())
    check("ajustado: igual a adjust_uint16 sobre la maestra", s == 200 and diff <= 1, f"{s}, {diff} niveles")
    check("nombre ajustado", r["name"] == f"{PHOTO}-adjusted{suffix}" and r["adjusted"] is True, r["name"])

    assert 120 != default and 120 <= manifest["max"], "120 tiene que ser distinto de la final"
    s, r = prepare(adjust=ALL_ON, under_eyes=120)
    got = decode(download(r["id"])).astype(np.int32)
    want = adjust.adjust_uint16(editor_server.blend_eyes(crop, PHOTO, x, y, 120, manifest), adjust.parse(ALL_ON))
    diff = int(np.abs(got - want).max())
    check("ajustado con ojeras al 120: los pixeles", s == 200 and diff <= 1, f"{s}, {diff} niveles")
    check("nombre ajustado con ojeras", r["name"] == f"{PHOTO}-adjusted-under-eyes-120{suffix}", r["name"])

    s, r = prepare(adjust=ALL_ON, under_eyes=120, version="Version 2")
    check("nombre con version", s == 200 and r["name"] == f"{PHOTO}-version-2{suffix}" and r["version"] == "version-2",
          r.get("name"))

    s, r = prepare(image="raw", adjust=ALL_ON, version="Version 2")
    check("el RAW ignora ajustes y version", s == 200 and r["name"] == f"{PHOTO}-raw{suffix}" and not r["adjusted"], r.get("name"))

    bad = {"clave desconocida": {"adjust": {"glow": 10}}, "101": {"adjust": {"contrast": 101}},
           "exposicion 3": {"adjust": {"exposure": 3}}, "NaN en texto": {"adjust": {"contrast": "NaN"}},
           "True": {"adjust": {"contrast": True}}, "version de 41": {"version": "v" * 41}, "version numero": {"version": 2},
           "fondo con clave desconocida": {"background": {"glow": 10}}, "fondo parejo 150": {"background": {"evenness": 150}},
           "fondo parejo negativo": {"background": {"evenness": -1}}, "fondo como lista": {"background": [1, 2]}}
    for name, extra in bad.items():
        s, r = prepare(**extra)
        check(f"prepare rechaza {name}", s == 400, f"{s} {r}")


def test_backdrop() -> None:
    """El fondo: lo mismo que backdrop.render sobre la maestra, en un recorte con pared, pelo y cara."""
    cx, cy, rx, ry = PHOTOS[PHOTO]["faces"][0]["oval"][:4]
    w = h = 1024
    x, y = int(cx - w / 2), int(max(cy - ry - h / 2, 0))
    full = tifffile.imread(ROOT / "editadas" / f"{PHOTO}.tif")
    H, W = full.shape[:2]
    crop = full[y : y + h, x : x + w].copy()
    del full
    manifest = editor_server.eye_manifest()[0]
    layers = backdrop.load_layers(PHOTO)
    a = layers.alpha16[y : y + h, x : x + w]
    check("fondo: el recorte tiene pared, borde y persona", (a == 0).any() and ((a > 0) & (a < 65535)).any() and (a == 65535).any())
    box, suffix = [x, y, w, h], f"-crop-{w}x{h}.png"

    s0, r0 = prepare(box=box)
    s1, r1 = prepare(box=box, background={k: 0 for k in backdrop.KEYS})
    check("fondo en 0: identico a sin fondo", s0 == s1 == 200 and download(r0["id"]) == download(r1["id"]) and r1["backdrop"] is False)

    for name, extra in {"solo el fondo": {}, "fondo y ajustes": {"adjust": ALL_ON}}.items():
        s, r = prepare(box=box, background=BG_ON, **extra)
        got = decode(download(r["id"])).astype(np.int32)
        eyes = editor_server.blend_eyes(crop, PHOTO, x, y, manifest["intensity"], manifest)
        want = backdrop.render(eyes, x, y, (H, W), layers, adjust.parse(extra.get("adjust")), backdrop.parse(BG_ON)).astype(np.int32)
        diff = np.abs(got - want)
        check(f"{name}: igual a backdrop.render", s == 200 and int(diff.max()) <= 1, f"{s}, {int(diff.max())} niveles")
        check(f"{name}: la gente como sin fondo", s == 200 and np.array_equal(
            got[a == 65535], adjust.adjust_uint16(eyes, adjust.parse(extra.get("adjust")))[a == 65535].astype(np.int32)))
        check(f"{name}: avisa el fondo y el nombre dice ajustado", r.get("backdrop") is True and r["name"] == f"{PHOTO}-adjusted{suffix}", r.get("name"))

    s, r = prepare(box=box, image="raw", background=BG_ON)
    check("el RAW ignora el fondo", s == 200 and r["backdrop"] is False and r["name"] == f"{PHOTO}-raw{suffix}", r.get("name"))


def test_dng() -> None:
    """El DNG ("RAW export"): los datos del TIFF en luz lineal, con las etiquetas DNG, sin ICC ni Orientation, y LibRaw
    (rawpy) lo lee de vuelta a 2 de 65535 como mucho (lo medido el 2026-10-14). LibRaw va con adjust_maximum_thr=0: por
    defecto, si el pixel mas claro pasa el 75 % del blanco, toma ese pixel como blanco y aclara todo (medido: un recorte
    del RAW original sin blancos salia 2,7 % mas claro), aunque el archivo dice WhiteLevel 65535."""
    import io

    import rawpy

    for image in ("edit", "raw"):
        extra = {"adjust": ALL_ON, "background": BG_ON} if image == "edit" else {}
        s1, r1 = prepare(image=image, format="tiff", **extra)
        s2, r2 = prepare(image=image, format="dng", **extra)
        if not (s1 == s2 == 200):
            check(f"dng {image}: prepare", False, f"{s1} {s2} {r2}")
            continue
        tif, dng = download(r1["id"]), download(r2["id"])
        srgb = tifffile.imread(io.BytesIO(tif)).astype(np.uint16)
        if image == "raw":  # el RAW original es de 8 bits: el TIFF sale a 8, el DNG con esos 8 llevados a 16
            srgb = srgb * 257
        want = (editor_server.TO_LINEAR[srgb] * 65535 + 0.5).astype(np.uint16)
        with tifffile.TiffFile(io.BytesIO(dng)) as t:
            page = t.pages[0]
            got, tags = page.asarray(), page.tags
            meta = {"photometric": int(page.photometric), "version": tags.get(50706) and tuple(tags[50706].value),
                    "matrix": 50721 in tags, "forward": 50964 in tags, "icc": 34675 in tags, "orientation": 274 in tags}
        check(f"dng {image}: los pixeles del TIFF en luz lineal, 16 bits", got.dtype == np.uint16 and np.array_equal(got, want),
              f"{got.dtype} {got.shape} max {int(np.abs(got.astype(np.int32) - want).max()) if got.shape == want.shape else '-'}")
        check(f"dng {image}: LinearRaw con DNGVersion 1.4 y las matrices, sin ICC ni Orientation",
              meta == {"photometric": 34892, "version": (1, 4, 0, 0), "matrix": True, "forward": True, "icc": False, "orientation": False},
              str(meta))
        with rawpy.imread(io.BytesIO(dng)) as raw:
            lib = raw.postprocess(gamma=(1, 1), no_auto_bright=True, output_bps=16, use_camera_wb=False, user_wb=[1, 1, 1, 1],
                                  output_color=rawpy.ColorSpace.raw, user_flip=0, adjust_maximum_thr=0)
        d = int(np.abs(lib.astype(np.int32) - want).max()) if lib.shape == want.shape else None
        check(f"dng {image}: LibRaw lo lee a 2 de 65535 como mucho", d is not None and d <= 2, f"{lib.shape} max {d}")
        stem = r1["name"].rsplit(".", 1)[0]
        check(f"dng {image}: el nombre del TIFF con .dng y los bits del origen",
              r2["name"] == f"{stem}.dng" and r2["bits"] == (16 if image == "edit" else 8), f"{r2['name']} {r2['bits']}")


def mirror(box: list) -> list:
    """La misma caja en la foto espejada: lo que se ve en (x, y) con Flip es lo de (W - x - w, y) sin Flip."""
    x, y, w, h = box
    return [_W - x - w, y, w, h]


def test_flip() -> None:
    """Flip (2026-10-20): el archivo es el espejo del de la caja espejada; con fondo, la caida va al borde derecho de lo
    que se ve (backdrop.render sobre la maestra y las capas espejadas); sin flip, byte a byte lo de siempre."""
    import io

    import rawpy

    s0, r0 = prepare(adjust=ALL_ON)
    s1, r1 = prepare(adjust=ALL_ON, flip=False)
    check("flip false: el mismo archivo que sin el campo", s0 == s1 == 200 and download(r0["id"]) == download(r1["id"])
          and r1["name"] == r0["name"] and r1["flip"] is False, r1.get("name"))

    # con ojeras movidas y los once ajustes, todo por pixel: espejo exacto a tamano real, y en la cara
    for image, extra in (("edit", {"adjust": ALL_ON, "under_eyes": 120}), ("raw", {})):
        sa, ra = prepare(image=image, **extra)
        sb, rb = prepare(image=image, box=mirror(BOX), flip=True, **extra)
        a, b = decode(download(ra["id"])), decode(download(rb["id"]))
        d = int(np.abs(b.astype(np.int32) - a[:, ::-1]).max()) if a.shape == b.shape else None
        stem = ra["name"].replace("-crop-", "-flip-crop-")
        check(f"flip {image}: el espejo exacto del de la caja espejada, -flip en el nombre",
              sa == sb == 200 and d == 0 and rb["name"] == stem and rb["flip"] is True, f"max {d} · {rb.get('name')}")

    # achicado (INTER_AREA espejado redondea distinto en el ultimo bit): hasta 1 nivel de 65535
    big = [BOX[0], BOX[1], min(1500, _W - BOX[0]), min(1500, _H - BOX[1])]
    sa, ra = prepare(box=big, size=1024, adjust=ALL_ON)
    sb, rb = prepare(box=mirror(big), size=1024, adjust=ALL_ON, flip=True)
    a, b = decode(download(ra["id"])), decode(download(rb["id"]))
    d = int(np.abs(b.astype(np.int32) - a[:, ::-1]).max()) if a.shape == b.shape else None
    check("flip achicado a 1024: el espejo, hasta 1 de 65535", sa == sb == 200 and d is not None and d <= 1, f"max {d}")

    # el fondo: la maestra y las capas espejadas, recortadas en la x de lo que se ve. Con caida, en una caja del borde
    full = tifffile.imread(ROOT / "editadas" / f"{PHOTO}.tif")
    ftif = np.ascontiguousarray(full[:, ::-1])
    del full
    lay = backdrop.load_layers(PHOTO)
    flipped = backdrop.Layers(np.ascontiguousarray(lay.alpha16[:, ::-1]), np.ascontiguousarray(lay.behind16[:, ::-1]),
                              np.ascontiguousarray(lay.light[:, ::-1]), lay.top)
    light = {"exposure": -0.2, "contrast": 20}
    for label, box in (("cara y pelo", BOX), ("pared del borde", [_W - 1024, 0, 1024, 1024]), ("pared del otro borde", [0, 0, 1024, 1024])):
        x, y, w, h = box
        s, r = prepare(box=box, adjust=light, background=BG_ON, flip=True)  # ojeras en la final: sin parches
        got = decode(download(r["id"])).astype(np.int32)
        want = backdrop.render(ftif[y : y + h, x : x + w], x, y, ftif.shape[:2], flipped, adjust.parse(light), backdrop.parse(BG_ON))
        d = int(np.abs(got - want).max())
        check(f"flip con fondo, {label}: backdrop.render sobre la maestra y las capas espejadas (hasta 2 de 65535)",
              s == 200 and r["backdrop"] and r["flip"] and d <= 2, f"max {d} · {r.get('name')}")
    # la caida va al borde derecho de lo que se ve: no es el espejo del archivo sin Flip
    box = [0, 0, 1024, 1024]
    sa, ra = prepare(box=mirror(box), adjust=light, background=BG_ON)
    sb, rb = prepare(box=box, adjust=light, background=BG_ON, flip=True)
    a, b = decode(download(ra["id"])), decode(download(rb["id"]))
    check("flip con caida: la caida queda a la derecha de lo que se ve (no es el espejo del de siempre)",
          int(np.abs(b.astype(np.int32) - a[:, ::-1]).max()) > 1000)
    del ftif, flipped, lay

    # DNG: los pixeles espejados, sin tag Orientation; leido de vuelta con tifffile y con LibRaw
    sa, ra = prepare(format="dng")
    sb, rb = prepare(format="dng", box=mirror(BOX), flip=True)
    x, y = download(ra["id"]), download(rb["id"])
    tx, ty = tifffile.imread(io.BytesIO(x)), tifffile.imread(io.BytesIO(y))
    with tifffile.TiffFile(io.BytesIO(y)) as tf:
        orientation = tf.pages[0].tags.get(274)

    def libraw(data):
        with rawpy.imread(io.BytesIO(data)) as raw:
            return raw.postprocess(gamma=(1, 1), no_auto_bright=True, output_bps=16, use_camera_wb=False, user_wb=[1, 1, 1, 1],
                                   output_color=rawpy.ColorSpace.raw, adjust_maximum_thr=0)
    lx, ly = libraw(x), libraw(y)
    check("flip DNG: los pixeles espejados, sin Orientation (tifffile y LibRaw, espejo exacto)",
          np.array_equal(ty, tx[:, ::-1]) and np.array_equal(ly, lx[:, ::-1]) and orientation is None and rb["name"].endswith(".dng")
          and "-flip-" in rb["name"], rb.get("name"))
    for name, value in {"1": 1, "texto": "true", "null": None, "lista": [True]}.items():
        s, r = prepare(flip=value)
        check(f"prepare rechaza flip {name}", s == 400, f"{s} {r}")


def test_shape() -> None:
    """La forma (2026-10-23): el circulo es la misma caja cuadrada con el circulo inscripto como transparencia. Los
    colores, los del archivo cuadrado sin tocar; el alpha, 0 en las esquinas y entero en el medio. JPG y DNG salen
    cuadrados; una caja que no es cuadrada, 400."""
    import io

    from PIL import Image

    def rgba_png(data: bytes) -> np.ndarray:
        return cv2.cvtColor(cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)

    def circle(n: int) -> np.ndarray:  # el circulo, calculado aparte: cuanto del pixel cae adentro del radio, en 4x4 muestras
        t = (np.arange(n * 4) + 0.5) / 4 - n / 2
        inside = (t[None, :] ** 2 + t[:, None] ** 2 <= (n / 2) ** 2).reshape(n, 4, n, 4).mean(axis=(1, 3))
        return inside

    s0, r0 = prepare(adjust=ALL_ON)
    s1, r1 = prepare(adjust=ALL_ON, shape="square")
    check("shape square: el mismo archivo que sin el campo", s0 == s1 == 200 and download(r0["id"]) == download(r1["id"])
          and r1["name"] == r0["name"] and r1["shape"] == "square", r1.get("name"))
    square = decode(download(r0["id"]))
    n = BOX[2]

    s, r = prepare(adjust=ALL_ON, shape="circle")
    got = rgba_png(download(r["id"])) if s == 200 else None
    a = got[..., 3].astype(np.int32) if got is not None else None
    corners = a is not None and all(a[i, j] == 0 for i in (0, n - 1) for j in (0, n - 1))
    check("circulo PNG: 16 bits RGBA, los colores del cuadrado sin tocar, esquinas en 0 y el medio en 65535",
          s == 200 and got.dtype == np.uint16 and got.shape == (n, n, 4) and np.array_equal(got[..., :3], square)
          and corners and a[n // 2, n // 2] == 65535 and r["shape"] == "circle", f"{s} {r}")
    # la rampa por distancia no es el area exacta: medido, hasta 0,12 y 0,03 de media en el borde. Medio pixel corrido da
    # 0,81 y 0,33
    inside = circle(n)
    edge = (inside > 0) & (inside < 1)
    e = np.abs(a / 65535 - inside) if a is not None else None
    check("circulo PNG: el borde suavizado a un pixel (contra el area del pixel adentro del radio: hasta 0,15, media 0,05)",
          e is not None and e.max() <= 0.15 and e[edge].mean() <= 0.05, f"max {e.max() if e is not None else '-'}, media {e[edge].mean() if e is not None else '-'}")
    check("circulo: -circle al final del nombre", r["name"] == r0["name"].replace(".png", "-circle.png"), r.get("name"))

    # TIFF: el alpha sin premultiplicar (extrasamples) y los mismos colores
    s, r = prepare(adjust=ALL_ON, shape="circle", format="tiff")
    data = download(r["id"])
    with tifffile.TiffFile(io.BytesIO(data)) as tf:
        page = tf.pages[0]
        t, extra = page.asarray(), page.extrasamples
    check("circulo TIFF: RGBA de 16 bits sin premultiplicar, el mismo alpha y los mismos colores que el PNG",
          t.shape == (n, n, 4) and t.dtype == np.uint16 and tuple(extra) == (2,) and np.array_equal(t, got)
          and r["name"].endswith("-circle.tif"), f"{t.shape} {extra} {r.get('name')}")

    # WebP sin perdida: a 8 bits, con el color debajo de las esquinas transparentes (exact)
    s, r = prepare(adjust=ALL_ON, shape="circle", format="webp")
    sq_s, sq_r = prepare(adjust=ALL_ON, format="webp")
    w8 = np.asarray(Image.open(io.BytesIO(download(r["id"]))))
    sq8 = np.asarray(Image.open(io.BytesIO(download(sq_r["id"]))).convert("RGB"))
    want = ((got[..., 3].astype(np.uint32) + 128) // 257).astype(np.uint8)
    check("circulo WebP: RGBA de 8 bits, los colores del WebP cuadrado y el alpha del PNG a 8 bits",
          w8.shape == (n, n, 4) and np.array_equal(w8[..., :3], sq8) and np.array_equal(w8[..., 3], want)
          and r["name"].endswith("-circle.webp"), f"{w8.shape} {r.get('name')}")

    # achicado: la transparencia se hace al tamano del archivo, no se achica
    big = min(_W - BOX[0], _H - BOX[1], 2400)
    s, r = prepare(box=[BOX[0], BOX[1], big, big], size=1024, shape="circle")
    sq_s, sq_r = prepare(box=[BOX[0], BOX[1], big, big], size=1024)
    small, sq = rgba_png(download(r["id"])), decode(download(sq_r["id"]))
    check(f"circulo de {big} a 1024: los colores del cuadrado achicado y el circulo de 1024",
          s == 200 and small.shape == (1024, 1024, 4) and np.array_equal(small[..., :3], sq)
          and np.array_equal(small[..., 3], editor_server.circle_alpha(1024)[..., 0]) and r["name"].endswith("-1024x1024-circle.png"),
          f"{small.shape} {r.get('name')}")

    # el RAW original, a 8 bits como siempre, con el circulo
    s, r = prepare(image="raw", shape="circle")
    raw = rgba_png(download(r["id"]))
    sq_s, sq_r = prepare(image="raw")
    check("circulo del RAW original: PNG de 8 bits RGBA, los colores del cuadrado",
          s == 200 and raw.dtype == np.uint8 and raw.shape == (n, n, 4) and np.array_equal(raw[..., :3], decode(download(sq_r["id"])))
          and r["name"].endswith("-raw-crop-%dx%d-circle.png" % (n, n)), f"{raw.dtype} {r.get('name')}")

    # con Flip: el circulo sobre el archivo espejado
    s, r = prepare(adjust=ALL_ON, box=mirror(BOX), flip=True, shape="circle")
    fl = rgba_png(download(r["id"]))
    check("circulo con Flip: el espejo del cuadrado y el mismo circulo, -flip y -circle",
          s == 200 and np.array_equal(fl[..., :3], square[:, ::-1]) and np.array_equal(fl[..., 3], got[..., 3])
          and "-flip-" in r["name"] and r["name"].endswith("-circle.png"), r.get("name"))

    # JPG y DNG no tienen transparencia: el mismo archivo que el cuadrado, sin -circle
    for fmt in ("jpeg", "dng"):
        sa, ra = prepare(adjust=ALL_ON, format=fmt)
        sb, rb = prepare(adjust=ALL_ON, format=fmt, shape="circle")
        check(f"circulo en {fmt}: sale cuadrado, el mismo archivo", sa == sb == 200 and rb["name"] == ra["name"]
              and download(ra["id"]) == download(rb["id"]) and rb["shape"] == "square", rb.get("name"))

    s, r = prepare(box=[BOX[0], BOX[1], BOX[2], BOX[3] - 1], shape="circle")
    check("circulo con una caja que no es cuadrada: 400", s == 400, f"{s} {r}")
    for name, value in {"ovalo": "oval", "numero": 1, "null": None, "lista": ["circle"]}.items():
        s, r = prepare(shape=value)
        check(f"prepare rechaza shape {name}", s == 400, f"{s} {r}")


def test_versions() -> None:
    VERSIONS.unlink(missing_ok=True)
    s, hd, data = call("GET", "/api/versions")
    check("versiones: sin archivo, vacio", s == 200 and json.loads(data) == {"photos": {}}, f"{s} {data!r}")
    check("versiones: no-store", hd.get("Cache-Control") == "no-store", str(hd.get("Cache-Control")))

    one, two = state(3), state(1, None)
    s, _, data = call("POST", "/api/versions", {"photo": PHOTO, "state": one})
    check("versiones: guardar", s == 200 and json.loads(data) == {"ok": True}, f"{s} {data!r}")
    s, _, data = call("GET", "/api/versions")
    check("versiones: ida y vuelta", s == 200 and json.loads(data) == {"photos": {PHOTO: one}})
    saved = {PHOTO: one}
    if OTHER:
        s, _, _ = call("POST", "/api/versions", {"photo": OTHER, "state": two})
        s2, _, data = call("GET", "/api/versions")
        saved[OTHER] = two
        check("versiones: guardar otra foto deja la primera", s == s2 == 200 and json.loads(data) == {"photos": saved})

    good = {"photo": PHOTO, "state": one}
    cases = {
        "Host ajeno": (403, dict(headers={"Host": f"evil.example:{PORT}"}, body=good)),
        "Origin ajeno": (403, dict(headers={"Origin": "http://evil.example"}, body=good)),
        "Content-Type": (415, dict(headers={"Content-Type": "text/plain"}, body=good)),
        "mas de 65536 bytes": (413, dict(headers={"Content-Length": "65537"}, raw=b"")),
        "foto desconocida": (400, dict(body={"photo": "NO-SUCH-PHOTO", "state": one})),
        "clave de mas en el estado": (400, dict(body={"photo": PHOTO, "state": one | {"extra": 1}})),
        "clave de mas en el pedido": (400, dict(body=good | {"extra": 1})),
        "activePresetId ajeno": (400, dict(body={"photo": PHOTO, "state": one | {"activePresetId": "preset-zz"}})),
        "41 versiones": (400, dict(body={"photo": PHOTO, "state": state(41)})),
        "valor infinito": (400, dict(raw=json.dumps({"photo": PHOTO, "state": one | {"values": {"a": float("inf")}}}).encode())),
        "JSON roto": (400, dict(raw=b"{nope")),
    }
    for name, (want, kw) in cases.items():
        s, _, data = call("POST", "/api/versions", **kw)
        check(f"versiones rechaza {name}", s == want, f"{s} {data[:80]!r}")
    s, _, data = call("GET", "/api/versions")
    check("versiones: lo rechazado no se guardo", json.loads(data) == {"photos": saved})

    VERSIONS.write_text(f'{{"photos": {{"{PHOTO}": ')  # a medio escribir
    s, _, data = call("GET", "/api/versions")
    check("versiones corruptas: GET da 500 en JSON", s == 500 and "error" in json.loads(data), f"{s}")
    s, _, data = call("POST", "/api/versions", good)
    check("versiones corruptas: POST da 500 y no pisa el archivo",
          s == 500 and VERSIONS.read_text() == f'{{"photos": {{"{PHOTO}": ', f"{s}")
    check("versiones: no quedan temporales", not list(VERSIONS.parent.glob(".versiones-*")))


def main() -> int:
    backup = VERSIONS.read_bytes() if VERSIONS.exists() else None
    env = os.environ | {"MallocLargeCache": "0"}
    log = tempfile.TemporaryFile("w+")  # el log del servidor: solo se muestra si algo fallo
    server = subprocess.Popen(["nice", "-n", "19", sys.executable, str(ROOT / "recipe" / "editor_server.py"), str(PORT)],
                              cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=log)
    try:
        wait_ready(server)
        test_prepare()
        test_backdrop()
        test_dng()
        test_flip()
        test_shape()
        test_versions()
    finally:
        server.terminate()
        try:
            server.wait(10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
        if backup is None:
            VERSIONS.unlink(missing_ok=True)
        else:
            VERSIONS.write_bytes(backup)
    if failed:
        log.seek(0)
        print(log.read(), end="")
        print(f"fallaron {len(failed)}: {', '.join(failed)}")
        return 1
    print("todo bien")
    return 0


if __name__ == "__main__":
    sys.exit(main())
