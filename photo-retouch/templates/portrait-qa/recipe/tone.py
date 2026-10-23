"""Curvas de tono en L*: monotonas, con pendiente limitada, ajustadas por pares medidos."""

import numpy as np


def lstar(y: np.ndarray) -> np.ndarray:
    y = np.maximum(y, 0)
    return np.where(y > 0.008856, 116 * np.cbrt(y) - 16, 903.3 * y)


def y_from(lstar_: np.ndarray) -> np.ndarray:
    lstar_ = np.clip(lstar_, 0, 100)
    return np.where(lstar_ > 8, ((lstar_ + 16) / 116) ** 3, lstar_ / 903.3)


def pchip(xk: np.ndarray, yk: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Interpolacion monotona (Fritsch-Carlson): la curva nunca se da vuelta ni rebota."""
    h = np.diff(xk)
    d = np.diff(yk) / h
    m = np.zeros_like(yk)
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, len(xk) - 1):
        if d[i - 1] * d[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    xc = np.clip(x, xk[0], xk[-1])
    i = np.clip(np.searchsorted(xk, xc) - 1, 0, len(xk) - 2)
    t = (xc - xk[i]) / h[i]
    h00, h10, h01, h11 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t, -2 * t**3 + 3 * t**2, t**3 - t**2
    return h00 * yk[i] + h10 * h[i] * m[i] + h01 * yk[i + 1] + h11 * h[i] * m[i + 1]


def isotonic(values: list[float], weights: list[float]) -> list[float]:
    """Pool adjacent violators: la salida mas parecida a `values` que nunca baja."""
    blocks = [[v, w, 1] for v, w in zip(values, weights)]
    i = 0
    while i < len(blocks) - 1:
        if blocks[i][0] > blocks[i + 1][0]:
            v1, w1, c1 = blocks[i]
            v2, w2, c2 = blocks[i + 1]
            blocks[i] = [(v1 * w1 + v2 * w2) / (w1 + w2), w1 + w2, c1 + c2]
            del blocks[i + 1]
            i = max(i - 1, 0)
        else:
            i += 1
    out = []
    for v, _, c in blocks:
        out += [v] * c
    return out


def fit_curve(inp: dict, want: dict, weights: dict, pivot: str) -> tuple[np.ndarray, np.ndarray]:
    """Curva que pasa por cada par (entrada -> objetivo). `pivot` es el punto que queda fijo al limitar la pendiente."""
    pairs = sorted(((min(inp[k], 99.0), want[k], weights[k]) for k in weights), key=lambda t: t[0])
    xs = [p[0] for p in pairs]
    ys = isotonic([p[1] for p in pairs], [p[2] for p in pairs])
    # puntos casi iguales en la entrada se juntan (la curva no puede ser vertical)
    xk, yk = [0.0], [max(0.0, ys[0] - xs[0] * 0.15)]
    for x, y in zip(xs, ys):
        if x - xk[-1] < 1.0:
            yk[-1] = max(yk[-1], y)
            continue
        xk.append(x)
        yk.append(max(y, yk[-1] + 0.05))
    xk.append(100.0)
    yk.append(min(100.0, max(yk[-1] + 0.05, yk[-1] + (100 - xk[-2]) * 1.0)))  # arriba del ultimo punto sigue a 45 grados
    return limit_slope(np.array(xk, np.float32), np.array(yk, np.float32), inp[pivot])


MAX_SLOPE = 3.0  # mas empinado que esto la piel se mancha (posterizado)
MIN_SLOPE = 0.15  # mas plano que esto se pierde el detalle


def limit_slope(xk: np.ndarray, yk: np.ndarray, anchor: float) -> np.ndarray:
    """Recorta la pendiente de cada tramo, dejando fija la cara (p75) y corriendo el resto.

    Cuando la foto no permite llegar a un objetivo sin una curva vertical (fondo tan
    claro como la cara y la referencia lo pide negro), gana la piel sin manchas y ese
    objetivo queda corto: la diferencia se ve en la hoja de comparacion.
    """
    i0 = int(np.argmin(np.abs(xk - anchor)))
    y = yk.copy()
    for i in range(i0, len(xk) - 1):
        dx = xk[i + 1] - xk[i]
        y[i + 1] = np.clip(y[i + 1], y[i] + MIN_SLOPE * dx, y[i] + MAX_SLOPE * dx)
    for i in range(i0, 0, -1):
        dx = xk[i] - xk[i - 1]
        y[i - 1] = np.clip(y[i - 1], y[i] - MAX_SLOPE * dx, y[i] - MIN_SLOPE * dx)
    return xk, np.clip(y, 0, 100)


