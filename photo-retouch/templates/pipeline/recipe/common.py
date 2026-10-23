"""Piezas compartidas: rutas, leer y guardar la base lineal, codificar a sRGB, Lab y PNG.

Todo el trabajo es en float32 lineal (primarios sRGB, D65) salido del RAW. No hay JPEG en
ningun paso: los intermedios son TIFF float16, las salidas TIFF de 16 bits y PNG.
"""

from pathlib import Path

import cv2
import numpy as np
import tifffile
from PIL import Image, ImageCms

ROOT = Path(__file__).resolve().parent.parent
WORK = ROOT / "work"
PROCESS = ROOT / "proceso"
NOTES = ROOT / "proceso-notas"  # notas, scripts archivados y numeros del proceso (las imagenes van a proceso/)
EDITED = ROOT / "editadas"

from photos import STUDIO  # noqa: E402  (photos.py no importa nada del proyecto: no hay ciclo)

PHOTO_NAMES = list(STUDIO)  # las de la sesion, con sus datos a mano en recipe/photos.py

LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def save_linear(img: np.ndarray, name: str, suffix: str) -> Path:
    """Intermedio lineal en float16: guarda negativos y valores sobre 1 sin recortar."""
    out = WORK / f"{name}-{suffix}.tif"
    out.parent.mkdir(parents=True, exist_ok=True)
    tifffile.imwrite(out, img.astype(np.float16), compression="zlib")
    return out


def load_linear(name: str, suffix: str) -> np.ndarray:
    return tifffile.imread(WORK / f"{name}-{suffix}.tif").astype(np.float32)


def luminance(img: np.ndarray) -> np.ndarray:
    return img @ LUMA


def linear_to_srgb(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055).astype(np.float32)


def srgb_to_linear(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.04045, x / 12.92, np.power((x + 0.055) / 1.055, 2.4)).astype(np.float32)


# --- Lab sobre lineal sRGB (D65), en float: sin pasar por 8 bits ---------------------
_RGB2XYZ = np.array(
    [[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]],
    np.float32,
)
_WHITE = np.array([0.95047, 1.0, 1.08883], np.float32)


def lab(img: np.ndarray) -> np.ndarray:
    xyz = (img @ _RGB2XYZ.T) / _WHITE
    xyz = np.maximum(xyz, 0)
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    L = 116 * f[..., 1] - 16
    a = 500 * (f[..., 0] - f[..., 1])
    b = 200 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], -1).astype(np.float32)


def lab_to_linear(lab_img: np.ndarray) -> np.ndarray:
    """Inversa de lab(): Lab (D65) -> sRGB lineal, en float."""
    L, a, b = lab_img[..., 0], lab_img[..., 1], lab_img[..., 2]
    fy = (L + 16) / 116
    fx, fz = fy + a / 500, fy - b / 200
    eps, kappa = 216 / 24389, 24389 / 27
    xyz = np.stack(
        [
            np.where(fx**3 > eps, fx**3, (116 * fx - 16) / kappa),
            np.where(L > kappa * eps, fy**3, L / kappa),
            np.where(fz**3 > eps, fz**3, (116 * fz - 16) / kappa),
        ],
        -1,
    ) * _WHITE
    return (xyz @ np.linalg.inv(_RGB2XYZ).T.astype(np.float32)).astype(np.float32)


def lightness(y: np.ndarray) -> np.ndarray:
    """L* de una luminancia lineal (0..1)."""
    y = np.maximum(y, 0)
    return np.where(y > 216 / 24389, 116 * np.cbrt(y) - 16, 24389 / 27 * y).astype(np.float32)


def lightness_to_y(L: float | np.ndarray) -> float | np.ndarray:
    L = np.asarray(L, np.float32)
    f = (L + 16) / 116
    return np.where(L > 8, f**3, L * 27 / 24389)


def blur(x: np.ndarray, sigma: float) -> np.ndarray:
    return cv2.GaussianBlur(x, (0, 0), sigma)


def norm_blur(x: np.ndarray, w: np.ndarray, sigma: float) -> np.ndarray:
    """Desenfoque que solo promedia donde w > 0 (piel, pared...): lo de afuera no se mete."""
    if x.ndim == 3:
        return blur(x * w[..., None], sigma) / (blur(w, sigma)[..., None] + 1e-6)
    return blur(x * w, sigma) / (blur(w, sigma) + 1e-6)


# --- salidas --------------------------------------------------------------------------
def _srgb_icc() -> bytes:
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def dither_noise(shape: tuple, seed: int = 0) -> np.ndarray:
    """El ruido del dither: triangular, de 1 LSB, y siempre el mismo para la misma forma. Un parche
    cortado de este campo cuantiza igual que la foto entera, asi no se le ve el borde."""
    rng = np.random.default_rng(seed)
    return rng.random(shape, np.float32) - rng.random(shape, np.float32)


def to_uint8(srgb: np.ndarray, dither: bool = True, seed: int = 0, noise: np.ndarray | None = None) -> np.ndarray:
    """A 8 bits con dither triangular de 1 LSB: sin esto el degrade de la pared hace escalones."""
    x = np.clip(srgb, 0, 1) * 255
    if dither:
        x = x + (dither_noise(x.shape, seed) if noise is None else noise)
    return np.clip(x + 0.5, 0, 255).astype(np.uint8)


def to_uint16(srgb: np.ndarray) -> np.ndarray:
    return (np.clip(srgb, 0, 1) * 65535 + 0.5).astype(np.uint16)


def save_png(srgb: np.ndarray, path: Path, dither: bool = True, noise: np.ndarray | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(to_uint8(srgb, dither, noise=noise)).save(path, icc_profile=_srgb_icc(), compress_level=6)


def save_tiff16(srgb: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tifffile.imwrite(path, to_uint16(srgb), compression="zlib", photometric="rgb", iccprofile=_srgb_icc())


def resize(img: np.ndarray, width: int) -> np.ndarray:
    h, w = img.shape[:2]
    return cv2.resize(img, (width, round(h * width / w)), interpolation=cv2.INTER_AREA)
