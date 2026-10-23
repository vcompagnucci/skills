"""El servidor del editor: sirve la carpeta y exporta desde la maestra de 16 bits.

Uso: .venv/bin/python recipe/editor_server.py [puerto]   (lo arranca Abrir editor.command)

El editor muestra los PNG de 8 bits de editadas/; exportar desde el navegador seria recortar
esos 8 bits. Aca el recorte sale del TIFF de 16 bits que escribe grade.py, se achica en luz
lineal y se codifica sin perdida: PNG y TIFF a 16 bits, WebP sin perdida a 8. Sin JPEG.
El RAW original ("antes") solo existe en PNG de 8 bits: se exporta a 8 bits.

El navegador pide /api/prepare apenas cambian las opciones; el archivo queda hecho en memoria y
la descarga (/api/file/<id>) sale al instante. Solo escucha en 127.0.0.1.

Ojeras: el editor deja mover su intensidad, de 0 a 200 %. La final sale a la de grade.py; para otra,
cada parche de editadas/ojeras/ se mezcla con la final hacia su punta (0 o 100 %), y pasado el 100 %,
la punta del 100 % con la del 200 %, en los mismos valores que mezcla el navegador: exacto en 0, en la
final, en 100 y en 200, y entre medio a menos de 1 % (README). Desde el 2026-10-19 cada cara tiene la suya: under_eyes
llega como {cara: intensidad}; un numero solo (una pagina vieja) vale para todas.

Luz y color: /api/prepare tambien recibe los ajustes del panel (adjust.py) y el nombre de la version
activa; se aplican sobre el recorte de 16 bits despues de las ojeras. Con todos en 0 sale identico.

Fondo: y la carpeta Background (backdrop.py), con las capas de editadas/fondo/: backdrop.render hace los
ajustes de la foto y despues la pared, como el shader. Sin fondo (o en 0), lo mismo que antes. La respuesta
dice "backdrop": un servidor de antes ignora el campo, y asi el editor se entera.

Versiones: /api/versions guarda el estado del panel de cada foto en editadas/versiones.json (GET lo lee,
POST reemplaza el de una foto y deja las otras). Se escribe entero a un temporal y se cambia de una vez;
si el archivo no se puede leer, no se pisa.
Importar: /api/import recibe un archivo (cualquier RAW o imagen, recipe/imports.py), lo deja en originales/ y lo
pone en una cola que corre recipe/import_photo.py de a una foto por vez, con nice y MallocLargeCache=0, como hijo de
este proceso (si el servidor se cierra, se corta). Si la Mac esta saturada (presion 4 o carga sobre 20), espera.
/api/imports dice en que paso esta cada una. La pagina (editor.html) se arma en cada pedido con las fotos que hay.
"""

import io
import json
import math
import os
import re
import signal
import struct
import subprocess
import sys
import time
import urllib.parse
import tempfile
import threading
import uuid
import zlib
from collections import OrderedDict
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import cv2
import numpy as np
import tifffile
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adjust  # noqa: E402
import backdrop  # noqa: E402
import imports  # noqa: E402
import viewer  # noqa: E402
from common import EDITED, ROOT, _srgb_icc, linear_to_srgb  # noqa: E402
from photos import PHOTOS, STUDIO, load_imports  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
SIZES = (1024, 2048, 4096)  # lado largo; "full" = los pixeles reales del recorte
FORMATS = {  # extension, tipo, bits del archivo
    "png": ("png", "image/png", 16),
    "tiff": ("tif", "image/tiff", 16),
    "webp": ("webp", "image/webp", 8),
    # pedido del fotografo el 2026-10-19 para entregar: solo sale por la descarga, nunca se escribe en el proyecto (.sin-jpg)
    "jpeg": ("jpg", "image/jpeg", 8),
}
JPEG_QUALITY = 95  # con color a resolucion completa (4:4:4): sin perdida visible, la mitad que a 100
IMAGES = ("edit", "raw")
EYES = EDITED / "ojeras"
MAX_BODY = 4096  # /api/prepare: los ajustes y el nombre de la version entran de sobra
MAX_VERSIONS_BODY = 65536
# las pruebas apuntan EDITOR_VERSIONS a una copia en work/: nunca tocan el archivo de verdad
VERSIONS = Path(os.environ["EDITOR_VERSIONS"]) if os.environ.get("EDITOR_VERSIONS") else EDITED / "versiones.json"
CONTROL = re.compile(r"[\x00-\x1f\x7f-\x9f]")
PRESET_ID = re.compile(r"preset-[A-Za-z0-9_-]{1,60}")
MAX_KEYS, MAX_KEY, MAX_TEXT, MAX_PRESETS, MAX_NAME = 64, 80, 64, 40, 40
KEEP_MASTERS = 2  # 150 MB cada una
KEEP_LAYERS = 1  # 210 MB cada una: el alpha y la pared de atras al tamano nativo
KEEP_FILES = 2  # el que se esta por bajar y el anterior
KEEP_RENDERED = 1  # la foto entera ya ajustada (150 MB): cambiar formato, tamano o recorte solo recorta y codifica

ICC = _srgb_icc()
masters: OrderedDict[tuple[str, str], tuple[tuple, np.ndarray]] = OrderedDict()
layer_cache: OrderedDict[str, tuple[tuple, backdrop.Layers]] = OrderedDict()
files: OrderedDict[str, tuple[bytes, str, str]] = OrderedDict()
rendered: OrderedDict[str, np.ndarray] = OrderedDict()
eye_patches: dict[Path, tuple[tuple, np.ndarray]] = {}
by_request: dict[str, dict] = {}
work = threading.Lock()  # un encode por vez: tocar opciones rapido no dispara diez en paralelo
tickets = threading.Lock()
latest = 0  # el pedido mas nuevo; uno que espera turno y ya quedo viejo no se codifica
saving = threading.Lock()  # aparte de `work`: guardar el panel no espera a una exportacion
TO_LINEAR = (lambda v: np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4))(
    np.arange(65536, dtype=np.float32) / 65535
).astype(np.float32)  # tabla: sin temporales de 26 MP


class Stale(Exception):
    pass


class Unreadable(Exception):
    """versiones.json existe pero no se puede leer: 500, y no se escribe encima."""


class NotReady(Exception):
    """La maestra se esta escribiendo (grade.py corriendo): se reintenta en un rato."""


def source(photo: str, image: str) -> tuple[Path, int, tuple]:
    """El archivo de origen, sus bits reales y su firma (si grade.py lo reescribe, la cache se entera)."""
    path, bits = (EDITED / f"{photo}.tif", 16) if image == "edit" else (EDITED / f"{photo}-antes.png", 8)
    try:
        s = path.stat()
    except FileNotFoundError:
        raise ValueError("no existe esa imagen") from None
    return path, bits, (path.name, s.st_mtime_ns, s.st_size)


def master(photo: str, image: str, path: Path, bits: int, sig: tuple) -> np.ndarray:
    """La imagen en uint16 RGB."""
    cached = masters.get((photo, image))
    if cached and cached[0] == sig:
        masters.move_to_end((photo, image))
        return cached[1]
    try:
        img = tifffile.imread(path) if bits == 16 else np.asarray(Image.open(path).convert("RGB")).astype(np.uint16) * 257
    except Exception as err:  # un archivo a medio escribir puede romper de mil formas
        raise NotReady from err
    if img is None or img.ndim != 3 or img.shape[2] != 3 or source(photo, image)[2] != sig:
        raise NotReady
    masters[(photo, image)] = (sig, img)
    while len(masters) > KEEP_MASTERS:
        masters.popitem(last=False)
    return img


def layer_sig(photo: str) -> tuple:
    """La firma de las capas del fondo de una foto (si styles.py las rehace, la cache se entera)."""
    try:
        return tuple((s.st_mtime_ns, s.st_size) for s in (path.stat() for path in backdrop.layer_paths(photo)))
    except FileNotFoundError:
        raise ValueError("el fondo de esa foto no esta hecho") from None


def layers(photo: str, sig: tuple) -> backdrop.Layers:
    cached = layer_cache.get(photo)
    if cached and cached[0] == sig:
        layer_cache.move_to_end(photo)
        return cached[1]
    try:
        found = backdrop.load_layers(photo)
    except Exception as err:  # a medio escribir
        raise NotReady from err
    if layer_sig(photo) != sig:
        raise NotReady
    layer_cache[photo] = (sig, found)
    while len(layer_cache) > KEEP_LAYERS:
        layer_cache.popitem(last=False)
    return found


def eye_manifest() -> tuple[dict, tuple]:
    """Donde va cada parche de ojeras, la intensidad de la final, el tope y su firma."""
    path = EYES / "ojeras.json"
    try:
        s = path.stat()
        return {"max": 100} | json.loads(path.read_text()), (s.st_mtime_ns, s.st_size)  # sin max: puntas de antes del 200 %
    except FileNotFoundError:
        return {"intensity": 100, "max": 100, "photos": {}}, (0, 0)
    except ValueError as err:  # grade.py lo esta escribiendo
        raise NotReady from err


def eye_patch(photo: str, face: str, tag: str) -> np.ndarray:
    path = EYES / f"{photo}-{face}-{tag}.tif"
    try:
        s = path.stat()
        sig = (s.st_mtime_ns, s.st_size)
        cached = eye_patches.get(path)
        if cached and cached[0] == sig:
            return cached[1]
        img = tifffile.imread(path)
    except Exception as err:  # falta o esta a medio escribir
        raise NotReady from err
    eye_patches[path] = (sig, img)
    return img


def eye_mix(level: int, manifest: dict) -> tuple[str | None, str, float] | None:
    """Entre que puntas va una intensidad: (desde, hasta, f). None en la de la final."""
    default = manifest["intensity"]
    if level == default:
        return None
    if level < default:
        return None, "0", 1 - level / default
    if level <= 100:
        return None, "100", (level - default) / (100 - default)
    return "100", str(manifest["max"]), (level - 100) / (manifest["max"] - 100)


def blend_eyes(crop: np.ndarray, photo: str, x: int, y: int, levels: int | dict, manifest: dict) -> np.ndarray:
    """La final, con las ojeras de cada cara a su %: cada parche entre la final y su punta, o pasado el 100 %,
    entre la punta del 100 % y la del tope. levels: {cara: %}, o un numero para todas."""
    faces = manifest["photos"].get(photo, [])
    if not isinstance(levels, dict):
        levels = {e["face"]: levels for e in faces}
    h, w = crop.shape[:2]
    out = None
    for e in faces:
        mix = eye_mix(levels.get(e["face"], manifest["intensity"]), manifest)
        if mix is None:
            continue
        start, tag, f = mix
        x0, y0 = max(e["x"], x), max(e["y"], y)
        x1, y1 = min(e["x"] + e["w"], x + w), min(e["y"] + e["h"], y + h)
        if x0 >= x1 or y0 >= y1:
            continue
        if out is None:
            out = crop.copy()  # el recorte es una vista de la maestra en cache
        inside = (slice(y0 - e["y"], y1 - e["y"]), slice(x0 - e["x"], x1 - e["x"]))
        end = eye_patch(photo, e["face"], tag)[inside].astype(np.float32)
        base = (out[y0 - y : y1 - y, x0 - x : x1 - x] if start is None else eye_patch(photo, e["face"], start)[inside]).astype(np.float32)
        out[y0 - y : y1 - y, x0 - x : x1 - x] = (base + f * (end - base) + 0.5).astype(np.uint16)
    return crop if out is None else out


def resample(crop: np.ndarray, out_w: int, out_h: int) -> np.ndarray:
    """Achica en luz lineal: promediar en sRGB oscurece el pelo fino sobre la pared clara."""
    if crop.shape[1] == out_w:
        return crop  # Full: los pixeles de la maestra, exactos
    small = linear_to_srgb(cv2.resize(TO_LINEAR[crop], (out_w, out_h), interpolation=cv2.INTER_AREA))
    return (small * 65535 + 0.5).astype(np.uint16)


def png_with_srgb(data: bytes) -> bytes:
    """OpenCV no marca el espacio de color: se agrega el bloque sRGB despues del encabezado."""
    chunk = b"sRGB" + b"\x00"
    block = struct.pack(">I", 1) + chunk + struct.pack(">I", zlib.crc32(chunk))
    return data[:33] + block + data[33:]


def encode(img: np.ndarray, fmt: str, bits: int) -> bytes:
    """img: uint16 RGB. bits: los del origen; el RAW original (8) se escribe a 8, como dice el dialogo."""
    if bits == 8 or fmt in ("webp", "jpeg"):
        img = ((img.astype(np.uint32) + 128) // 257).astype(np.uint8)
    if fmt == "png":
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        # compresion 1: sin perdida igual que la 3, 1 % mas pesado y medio segundo menos en la entera
        return png_with_srgb(cv2.imencode(".png", bgr, [cv2.IMWRITE_PNG_COMPRESSION, 1])[1].tobytes())
    if fmt == "tiff":
        buf = io.BytesIO()
        tifffile.imwrite(buf, img, photometric="rgb", compression="zlib", compressionargs={"level": 3},
                         predictor=True, iccprofile=ICC, resolution=(300, 300), resolutionunit="INCH")
        return buf.getvalue()
    buf = io.BytesIO()
    if fmt == "jpeg":
        Image.fromarray(img).save(buf, "JPEG", quality=JPEG_QUALITY, subsampling=0, optimize=True, progressive=True,
                                  icc_profile=ICC)
        return buf.getvalue()
    # sin perdida con method 0: los mismos pixeles, 3 veces mas rapido y ~25 % mas pesado que method 4
    Image.fromarray(img).save(buf, "WEBP", lossless=True, quality=60, method=0, exact=True, icc_profile=ICC)
    return buf.getvalue()


def slug(name: str) -> str:
    """El nombre de la version para el archivo: "Version 2" -> "version-2"."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40].strip("-")


def parse(req: dict) -> tuple[str, str, tuple[int, int, int, int], int | str, str, int | dict | None, dict, dict, str | None]:
    photo, image = req.get("photo"), req.get("image")
    if photo not in PHOTOS or image not in IMAGES:
        raise ValueError("foto invalida")
    box = req.get("box")
    if not (isinstance(box, list) and len(box) == 4 and all(type(v) is int for v in box)):
        raise ValueError("recorte invalido")
    size = req.get("size")
    if size != "full" and not (type(size) is int and size in SIZES):  # 1024.0 o True no pasan
        raise ValueError("tamano invalido")
    fmt = req.get("format")
    if fmt not in FORMATS:
        raise ValueError("formato invalido")
    level = req.get("under_eyes")  # None: la de la final (una pagina vieja no lo manda). Un numero: todas las caras
    ok = lambda v: type(v) is int and 0 <= v <= 200  # el tope real lo dice ojeras.json
    if image == "raw":
        level = None
    elif isinstance(level, dict):
        if not (len(level) <= 8 and all(isinstance(k, str) and ok(v) for k, v in level.items())):
            raise ValueError("intensidad de ojeras invalida")
    elif level is not None and not ok(level):
        raise ValueError("intensidad de ojeras invalida")
    params = adjust.parse(req.get("adjust"))  # lo que falta vale 0; fuera de rango, ValueError
    bg = backdrop.parse(req.get("background"))
    version = req.get("version")
    if version is not None and not (isinstance(version, str) and 1 <= len(version) <= 40 and not CONTROL.search(version)):
        raise ValueError("version invalida")
    if image == "raw":  # el RAW original sale como es: ni ajustes, ni fondo, ni version
        params, bg, version = adjust.parse(None), backdrop.parse(None), None
    return photo, image, tuple(box), size, fmt, level, params, bg, (slug(version) or None) if version else None  # "!!!" no deja nombre: va como sin version


def take_ticket() -> int:
    global latest
    with tickets:
        latest += 1
        return latest


def prepare(req: dict, ticket: int) -> dict:
    photo, image, (x, y, w, h), size, fmt, level, params, bg, version = parse(req)
    with_bg = not backdrop.is_neutral(bg)
    adjusted = not adjust.is_neutral(params) or with_bg
    path, bits, sig = source(photo, image)
    bg_sig = layer_sig(photo) if with_bg else None
    manifest, eyes_sig = eye_manifest()
    faces = [e["face"] for e in manifest["photos"].get(photo, [])]
    if image == "edit":
        if level is None:
            level = manifest["intensity"]
        if not isinstance(level, dict):
            level = {f: level for f in faces}
        elif set(level) != set(faces):
            raise ValueError("caras de ojeras invalidas")
        if any(v > manifest["max"] for v in level.values()):
            raise ValueError("intensidad de ojeras invalida")
        level = {f: level[f] for f in faces}  # en el orden de ojeras.json: la clave del pedido no depende del navegador
    key = json.dumps([photo, image, x, y, w, h, size, fmt, level, sig, eyes_sig, [params[k] for k in adjust.KEYS],
                      [bg[k] for k in backdrop.KEYS], bg_sig, version])
    with work:
        if key in by_request and by_request[key]["id"] in files:
            return by_request[key]
        if ticket != latest:
            raise Stale
        img = master(photo, image, path, bits, sig)
        H, W = img.shape[:2]
        if not (1 <= w <= W and 1 <= h <= H and 0 <= x <= W - w and 0 <= y <= H - h):
            raise ValueError("recorte fuera de la imagen")
        long = max(w, h)
        out = long if size == "full" else min(size, long)  # nunca se agranda
        out_w, out_h = max(1, round(w * out / long)), max(1, round(h * out / long))
        # la foto entera ajustada se guarda: con el mismo ajuste, otro formato, tamano o recorte sale de ahi. Cada pixel
        # se calcula igual entero que recortado (export_identical.py lo comprueba)
        look = json.dumps([photo, sig, eyes_sig, level, [params[k] for k in adjust.KEYS], [bg[k] for k in backdrop.KEYS], bg_sig])
        whole_img = rendered.get(look) if image == "edit" else None
        if whole_img is not None:
            rendered.move_to_end(look)
            crop = whole_img[y : y + h, x : x + w]
        else:
            crop = img[y : y + h, x : x + w]
            if image == "edit":
                crop = blend_eyes(crop, photo, x, y, level, manifest)
                if with_bg:
                    crop = backdrop.render(crop, x, y, (H, W), layers(photo, bg_sig), params, bg)
                elif adjusted:
                    crop = adjust.adjust_uint16(crop, params)
                if (w, h) == (W, H) and crop is not img:
                    rendered[look] = crop
                    while len(rendered) > KEEP_RENDERED:
                        rendered.popitem(last=False)
        data = encode(resample(crop, out_w, out_h), fmt, bits)
        ext, mime, file_bits = FORMATS[fmt]
        whole = (w, h) == (W, H)
        if image == "raw":
            tag = "-raw"
        elif version:  # el nombre de la version ya dice todo el ajuste
            tag = f"-{version}"
        else:
            moved = {f: v for f, v in level.items() if v != manifest["intensity"]}
            same = set(level.values())
            eyes = "" if not moved else f"-under-eyes-{level[faces[0]]}" if len(same) == 1 else \
                "-under-eyes-" + "-".join(f"{f}-{v}" for f, v in moved.items())
            tag = ("-adjusted" if adjusted else "") + eyes
        name = f"{photo}{tag}{'' if whole else '-crop'}-{out_w}x{out_h}.{ext}"
        fid = uuid.uuid4().hex
        files[fid] = (data, name, mime)
        while len(files) > KEEP_FILES:
            gone, _ = files.popitem(last=False)
            for k in [k for k, v in by_request.items() if v["id"] == gone]:
                del by_request[k]
        result = {"id": fid, "name": name, "bytes": len(data), "w": out_w, "h": out_h, "bits": min(bits, file_bits),
                  "under_eyes": level, "adjusted": adjusted, "backdrop": with_bg, "version": version}
        by_request[key] = result
        return result


def check_values(values) -> dict:
    """Los valores del panel: claves de texto y numeros finitos, si/no o textos cortos."""
    if not (isinstance(values, dict) and len(values) <= MAX_KEYS):
        raise ValueError("valores invalidos")
    for k, v in values.items():
        if not (isinstance(k, str) and len(k) <= MAX_KEY):
            raise ValueError("valores invalidos")
        if type(v) is bool or (isinstance(v, str) and len(v) <= MAX_TEXT):
            continue
        try:  # un entero enorme hace saltar a isfinite: tambien es invalido
            ok = type(v) in (int, float) and math.isfinite(v)
        except OverflowError:
            ok = False
        if not ok:
            raise ValueError("valores invalidos")
    return values


def check_state(state) -> dict:
    """El estado del panel de una foto, tal como lo guarda DialKit; nada de mas."""
    keys = {"version", "values", "baseValues", "presets", "activePresetId"}
    if not (isinstance(state, dict) and set(state) == keys):
        raise ValueError("estado invalido")
    if not (type(state["version"]) is int and state["version"] == 1):
        raise ValueError("version de estado invalida")
    check_values(state["values"])
    check_values(state["baseValues"])
    presets = state["presets"]
    if not (isinstance(presets, list) and len(presets) <= MAX_PRESETS):
        raise ValueError("versiones invalidas")
    ids = set()
    for pre in presets:
        if not (isinstance(pre, dict) and set(pre) == {"id", "name", "values"}):
            raise ValueError("version invalida")
        pid, name = pre["id"], pre["name"]
        if not (isinstance(pid, str) and PRESET_ID.fullmatch(pid)) or pid in ids:
            raise ValueError("id de version invalido")
        if not (isinstance(name, str) and 1 <= len(name) <= MAX_NAME and not CONTROL.search(name)):
            raise ValueError("nombre de version invalido")
        check_values(pre["values"])
        ids.add(pid)
    active = state["activePresetId"]
    if active is not None and active not in ids:
        raise ValueError("version activa invalida")
    return state


def read_versions() -> dict:
    """El archivo de versiones. Si no existe, vacio; si no se puede leer, OSError o ValueError (500): mejor
    no guardar nada que pisar las versiones de las otras fotos con un archivo a medias."""
    try:
        data = json.loads(VERSIONS.read_text())
    except FileNotFoundError:
        return {"photos": {}}
    if not (isinstance(data, dict) and isinstance(data.get("photos"), dict)):
        raise ValueError("versiones.json no tiene la forma esperada")
    return data


def save_version(req) -> None:
    if not (isinstance(req, dict) and set(req) == {"photo", "state"}):
        raise ValueError("pedido invalido")
    if req["photo"] not in PHOTOS:
        raise ValueError("foto invalida")
    state = check_state(req["state"])
    with saving:
        try:
            data = read_versions()
        except (OSError, ValueError) as err:
            raise Unreadable from err
        data["photos"][req["photo"]] = state
        fd, tmp = tempfile.mkstemp(dir=VERSIONS.parent, prefix=".versiones-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, VERSIONS)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise


# --- importar ------------------------------------------------------------------------------------------------------
jobs: list[str] = []  # claves en cola, en orden
job_state: dict[str, dict] = {}  # clave -> {"state": queued|waiting|running|done|failed, "step", "error"}
job_lock = threading.Condition()
child: subprocess.Popen | None = None
LOAD_MAX = 20.0  # el doble de los nucleos (CLAUDE.md > Recursos de la Mac)


def refresh_photos() -> None:
    """Las importadas terminadas entran al diccionario de fotos (el mismo objeto que leen todos los modulos)."""
    for k, v in load_imports().items():
        if k not in STUDIO and v.get("ready"):
            PHOTOS[k] = v


def mac_busy() -> bool:
    try:
        level = int(subprocess.run(["sysctl", "-n", "kern.memorystatus_vm_pressure_level"], capture_output=True, text=True).stdout)
    except ValueError:
        level = 1
    return level >= 4 or os.getloadavg()[0] > LOAD_MAX


def run_job(key: str) -> None:
    global child
    st = job_state[key]
    while mac_busy():
        st["state"] = "waiting"
        time.sleep(15)
    st.update(state="running", step="develop")
    env = {**os.environ, "MallocLargeCache": "0", "PYTHONUNBUFFERED": "1"}
    log_path = ROOT / "work" / "imports" / f"{key}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w") as log:
        child = subprocess.Popen(["nice", "-n", "19", sys.executable, str(Path(__file__).with_name("import_photo.py")), key],
                                 stdout=subprocess.PIPE, stderr=log, text=True, env=env, cwd=Path(__file__).parent)
        for line in child.stdout:
            if line.startswith("STEP "):
                st["step"] = line[5:].strip()
        code = child.wait()
        child = None
    if code == 0:
        refresh_photos()
        st.update(state="done", step="done")
    else:
        lines = [l for l in log_path.read_text().splitlines() if l.strip()]
        st.update(state="failed", error=(lines[-1] if lines else f"exit {code}")[:300])
        with imports.editing() as data:
            if key in data["photos"]:
                data["photos"][key]["error"] = st["error"]


def job_loop() -> None:
    while True:
        with job_lock:
            while not jobs:
                job_lock.wait()
            key = jobs[0]
        try:
            run_job(key)
        except Exception as err:  # el servidor sigue: la foto queda fallada
            job_state[key].update(state="failed", error=repr(err)[:300])
        with job_lock:
            jobs.pop(0)


def enqueue(key: str) -> None:
    with job_lock:
        job_state[key] = {"state": "queued", "step": None, "error": None}
        jobs.append(key)
        job_lock.notify()


def receive(handler, filename: str, length: int) -> dict:
    """El archivo, de a pedazos, a originales/<clave>.<ext>; despues a la cola."""
    kind = imports.kind(filename)
    if kind is None:
        ext = Path(filename).suffix.lower()
        raise ValueError("JPG is off in this project: no JPG at any step" if ext in imports.LOSSY
                         else f"{ext or 'That file'} isn't an image this editor reads")
    if not 0 < length <= imports.MAX_BYTES:
        raise ValueError("That file is too large")
    with imports.editing() as data:
        key = imports.new_key(filename, set(data["photos"]) | set(PHOTOS))
        labels = {v.get("label") or imports.label(k) for k, v in {**PHOTOS, **data["photos"]}.items()}
        tab = imports.label(key, labels)
        dest = imports.ORIGINALS / f"{key}{Path(filename).suffix.lower()}"
        data["photos"][key] = {"file": dest.name, "kind": kind, "label": tab, "name": Path(filename).name[:120],
                               "added": time.strftime("%Y-%m-%d %H:%M"), "ready": False}
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(f".{dest.name}.part")
    try:
        with open(tmp, "wb") as f:
            left = length
            while left:
                chunk = handler.rfile.read(min(left, 1 << 20))
                if not chunk:
                    raise ValueError("The upload was cut short")
                f.write(chunk)
                left -= len(chunk)
        tmp.replace(dest)
        dest.chmod(0o444)  # como los RAF: de solo lectura
    except BaseException:
        tmp.unlink(missing_ok=True)
        with imports.editing() as data:
            data["photos"].pop(key, None)
        raise
    enqueue(key)
    return {"key": key, "label": tab}


def import_status() -> dict:
    """Las que estan en camino o fallaron (las terminadas antes de arrancar el servidor no se listan)."""
    out = {}
    for k, v in load_imports().items():
        st = job_state.get(k)
        if v.get("ready") and not st:
            continue
        st = st or ({"state": "failed", "error": v["error"]} if v.get("error") else {"state": "queued"})
        out[k] = {"label": v.get("label", k), "name": v.get("name", k), **st}
    return out


def resume_imports() -> None:
    """Al arrancar: las que quedaron a medias (el servidor se cerro en el medio) vuelven a la cola."""
    for k, v in load_imports().items():
        if k not in STUDIO and not v.get("ready") and not v.get("error") and (imports.ORIGINALS / v.get("file", "")).is_file():
            enqueue(k)


def stop_child(*_):
    if child and child.poll() is None:
        child.terminate()
    raise SystemExit(0)


class Handler(SimpleHTTPRequestHandler):
    timeout = 30  # un pedido que promete mas cuerpo del que manda no deja el hilo colgado

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def local(self) -> bool:
        """Solo esta Mac y solo este origen: otra pagina abierta en el navegador no puede pedir nada."""
        port = self.server.server_address[1]
        if self.headers.get("Host") not in (f"127.0.0.1:{port}", f"localhost:{port}"):
            return False
        origin = self.headers.get("Origin")
        return origin is None or origin in (f"http://127.0.0.1:{port}", f"http://localhost:{port}")

    def end_headers(self):
        # las imagenes llevan ?v=<version> y no cambian sin cambiarlo; la pagina se revalida siempre
        path = getattr(self, "path", "")
        if path.startswith("/api/"):
            pass  # la API pone lo suyo
        elif "?v=" in path:
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        elif path.split("?")[0].endswith(".html") or path.endswith("/"):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_json(self, status: HTTPStatus, body: dict, no_store: bool = False) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        if no_store:
            self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        path = self.path.split("?")[0]
        if path == "/api/import":
            return self.post_import()
        limit = {"/api/prepare": MAX_BODY, "/api/versions": MAX_VERSIONS_BODY}.get(path)
        if limit is None or not self.local():
            return self.send_json(HTTPStatus.FORBIDDEN, {"error": "forbidden"})
        if self.headers.get("Content-Type") != "application/json":  # obliga al preflight de CORS
            return self.send_json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "json"})
        length = self.headers.get("Content-Length") or ""
        if not (length.isdigit() and 0 < int(length) <= limit):
            return self.send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "size"})
        try:
            req = json.loads(self.rfile.read(int(length)))
            if path == "/api/versions":
                save_version(req)
                return self.send_json(HTTPStatus.OK, {"ok": True})
            return self.send_json(HTTPStatus.OK, prepare(req, take_ticket()))
        except Unreadable as err:
            self.log_error("versiones: %r", err.__cause__)
            return self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "versiones.json no se puede leer"})
        except Stale:
            return self.send_json(HTTPStatus.CONFLICT, {"error": "stale"})
        except NotReady:
            return self.send_json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "rendering"})
        except (ValueError, TypeError, AttributeError) as err:
            return self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(err)})
        except Exception as err:  # cualquier otra cosa igual contesta: el navegador no se queda sin respuesta
            self.log_error("prepare: %r", err)
            return self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "server"})

    def post_import(self):
        if not self.local():
            return self.send_json(HTTPStatus.FORBIDDEN, {"error": "forbidden"})
        if self.headers.get("Content-Type") != "application/octet-stream":  # obliga al preflight de CORS
            return self.send_json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, {"error": "octet-stream"})
        name = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query).get("name", [""])[0]
        length = self.headers.get("Content-Length") or ""
        try:
            return self.send_json(HTTPStatus.OK, receive(self, name, int(length) if length.isdigit() else 0))
        except ValueError as err:
            self.close_connection = True  # el cuerpo puede no haberse leido
            return self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(err)})

    def send_page(self):
        try:
            data = viewer.page_html(viewer.visible()).encode()
        except Exception as err:
            self.log_error("pagina: %r", err)
            return self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "page"})
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_HEAD(self):
        if not self.local():
            return self.send_json(HTTPStatus.FORBIDDEN, {"error": "forbidden"})
        return super().do_HEAD()

    def do_GET(self):
        if not self.local():  # tambien frena el DNS rebinding: un dominio ajeno apuntado a 127.0.0.1
            return self.send_json(HTTPStatus.FORBIDDEN, {"error": "forbidden"})
        if self.path.split("?")[0] in ("/", "/editor.html"):
            return self.send_page()
        if not self.path.startswith("/api/"):
            return super().do_GET()
        if self.path.split("?")[0] == "/api/imports":
            return self.send_json(HTTPStatus.OK, import_status(), no_store=True)
        if self.path.split("?")[0] == "/api/versions":
            try:
                return self.send_json(HTTPStatus.OK, read_versions(), no_store=True)
            except Exception as err:  # corrupto o ilegible: se dice, no se inventa uno vacio
                self.log_error("versiones: %r", err)
                return self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "versiones.json no se puede leer"}, no_store=True)
        m = re.fullmatch(r"/api/file/([0-9a-f]{32})", self.path)
        entry = files.get(m.group(1)) if m else None
        if entry is None:
            return self.send_json(HTTPStatus.NOT_FOUND, {"error": "not found"})
        data, name, mime = entry
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", f'attachment; filename="{name}"')
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        # solo lo que fallo; log_error llega con un solo argumento (un timeout, un error al preparar)
        if len(args) < 2 or str(args[1]) not in ("200", "304"):
            super().log_message(fmt, *args)


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8775
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    refresh_photos()
    threading.Thread(target=job_loop, daemon=True).start()
    resume_imports()
    for sig in (signal.SIGTERM, signal.SIGHUP):  # cerrar la ventana de Terminal: la importacion en curso se corta
        signal.signal(sig, stop_child)
    print(f"Editor en http://127.0.0.1:{port}/editor.html (cerrá esta ventana para apagarlo)", flush=True)
    try:
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        if child and child.poll() is None:
            child.terminate()


if __name__ == "__main__":
    main()
