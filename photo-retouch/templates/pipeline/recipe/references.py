"""Referencias de estilo: de donde sale cada una y lo marcado a mano en ella para medirla.

Cada imagen esta en proceso/referencias-<id>.png. Se baja tal cual del sitio y se pasa a PNG en sRGB
(`import_reference`): el proyecto no tiene JPEG, y muchas vienen en Display P3, que leido como sRGB da
otros colores.

Lo marcado va en pixeles de esa imagen, leido en su grilla (tools/grid.py --ref <id>):
- faces: una elipse (cx, cy, rx, ry) por cara, de la frente al menton y de oreja a oreja, sin pelo;
- walls: recuadros (x0, y0, x1, y1) de fondo liso, lejos de la gente;
- blacks: recuadros de ropa negra o lo mas oscuro que haya, con luz pareja (sin pliegues hondos).
"""

import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

from common import PROCESS, srgb_to_linear

SRGB_ICC = "/System/Library/ColorSync/Profiles/sRGB Profile.icc"

REFS: dict[str, dict] = {
    # Los dos fundadores, remera negra y buzo azul: lo mas parecido a estas fotos. Fondo casi blanco.
    "ramp": {
        "source": "https://assets.ramp.com/nextjs/ramp_september_2026_media_kit.zip (leadership/ramp-founders.jpg)",
        "credit": "Ramp, media kit de septiembre de 2026 (https://ramp.com/press)",
        "faces": [(1545, 1475, 320, 480), (2700, 1890, 360, 480)],
        "walls": [(100, 300, 900, 1900), (3400, 300, 4700, 1800), (4350, 4300, 4750, 6500)],
        "blacks": [(1000, 3000, 1800, 4200)],  # la remera negra de Glyman
    },
    # Patrick Collison, buzo azul oscuro sobre fondo beige calido.
    "stripe": {
        "source": "https://downloads.stripeassets.com/fzn2n1nzq965/1jrj2urvAPvygVzm5pAo1o/7977b2726c54839a03e784280f315a0d/Stripe_Leadership.zip (Headshots/STRIPE_Patrick_Collison.jpg)",
        "credit": "Stripe, retratos de la direccion del newsroom (https://stripe.com/newsroom/information)",
        "faces": [(1845, 1875, 690, 960)],
        "walls": [(100, 300, 1000, 2100), (2950, 300, 3550, 2100)],
        "blacks": [(500, 3100, 1200, 4000), (2800, 3100, 3400, 4000)],  # el buzo azul oscuro
    },
    # John Ternus en la nota de Apple Newsroom de abril de 2026: pared gris que cae a negro.
    "apple": {
        "source": "https://www.apple.com/newsroom/images/2026/04/tim-cook-to-become-apple-executive-chairman-john-ternus-to-become-apple-ceo/article/Apple-John-Ternus.zip",
        "credit": "Apple Newsroom, 2026-04 (https://www.apple.com/newsroom/2026/04/tim-cook-to-become-apple-executive-chairman-john-ternus-to-become-apple-ceo/)",
        "faces": [(1453, 818, 290, 365)],
        # de la luz al negro: izquierda, derecha de la cabeza y el borde oscuro
        "walls": [(100, 200, 900, 1000), (2000, 200, 2400, 1500), (2550, 200, 2800, 1500)],
        "blacks": [(2600, 1800, 2860, 2400)],  # la camisa es gris jaspeado: lo mas oscuro es el fondo
    },
    # --- 2026-10-17, pedido: "busca referencias de foto del equipo, no en blanco y negro, de linear, apple, robinhood,
    # public, nothing". Los press kits no vienen en PNG: tools/ref_import.py los convierte a PNG sRGB en memoria.
    # Vlad Tenev, remera negra sobre blanco puro: lo mas parecido a estas fotos de todo el lote.
    "robinhood": {
        "source": "https://v.fastcdn.co/u/62ba1c13/65871811-0-Robinhood.-Leadershi.zip (Vlad Tenev)",
        "credit": "Robinhood, headshots de la direccion (https://press.robinhood.com/)",
        "faces": [(2890, 1890, 700, 800)],
        "walls": [(100, 100, 1500, 1400), (4200, 300, 5200, 2500), (4950, 3000, 5300, 4400)],
        "blacks": [(1500, 3700, 2500, 4500), (3500, 3800, 4200, 4600)],  # la remera negra
    },
    # Los dos cofundadores sentados en cajas de madera, fondo continuo blanco hueso calido. 2023.
    "public": {
        "source": "https://hellopublic.wpengine.com/wp-content/uploads/2023/10/Public-Media-Kit-2023.zip (Co-Founders - Headshot)",
        "credit": "Public, media kit 2023 (https://public.com/newsroom)",
        "faces": [(1630, 2090, 330, 400), (3610, 2570, 360, 450)],
        "walls": [(300, 300, 2000, 1400), (4800, 1000, 5800, 2800), (5450, 3800, 5950, 5200)],
        "blacks": [(3300, 3700, 4200, 4500)],  # el saco de terciopelo negro de Malling
    },
    # Carl Pei en la oficina, flash y pelicula. No hay pared lisa: "walls" son las cajas grises de plastico, que dicen
    # el tinte del revelado.
    "nothing": {
        "source": "https://cdn.shopify.com/s/files/1/0589/7168/5043/files/Carl_Pei.zip (Carl Pei 2)",
        "credit": "Nothing, brand assets 2022 (https://checkout.nothing.tech/pages/brand-assets)",
        "faces": [(1850, 830, 300, 300)],
        "walls": [(2800, 1100, 3500, 1800)],
        "blacks": [(1000, 2400, 1500, 3200), (1300, 4000, 2200, 4800)],  # la campera y el pantalon negros
    },
    # Johny Srouji en un laboratorio, camisa azul, fondo desenfocado frio. Abril de 2026.
    "apple-srouji": {
        "source": "https://www.apple.com/newsroom/images/2026/04/johny-srouji-named-apples-chief-hardware-officer/article/Apple-Johny-Srouji.zip",
        "credit": "Apple Newsroom, 2026-04 (https://www.apple.com/newsroom/2026/04/johny-srouji-named-apples-chief-hardware-officer/)",
        "faces": [(1870, 715, 290, 340)],
        "walls": [(200, 1100, 900, 1500), (3500, 50, 3800, 400)],  # el fondo desenfocado, no una pared
        "blacks": [(700, 2100, 1000, 2500)],  # la camisa azul oscura, lo mas oscuro con luz pareja
    },
    # Linear no publica fotos de equipo en color en alta: estas son cuadros de los videos de /careers (Cloudflare,
    # f=png). Remera negra de Linear en un escritorio, pared gris calida con caida suave.
    "linear": {
        "source": "https://linear.app/cdn-cgi/imagedelivery/fO02fVwohEs9s9UHFwon6A/73b4dc1e-fe1a-4d5e-86f9-194c393c6200/f=png,metadata=keep",
        "credit": "Linear, video de https://linear.app/careers",
        "faces": [(1075, 655, 190, 250)],
        "walls": [(1600, 150, 2400, 600), (1300, 650, 1650, 900), (2150, 650, 2700, 1000)],
        "blacks": [(750, 1100, 1150, 1300)],
    },
    # El mismo video: remera negra en un sillon de lino, pared blanca calida.
    "linear-sofa": {
        "source": "https://linear.app/cdn-cgi/imagedelivery/fO02fVwohEs9s9UHFwon6A/683284ee-470b-4aa2-3d3e-effe9d36d000/f=png,metadata=keep",
        "credit": "Linear, video de https://linear.app/careers",
        "faces": [(1555, 600, 215, 240)],
        "walls": [(300, 300, 1100, 1000), (2100, 300, 3300, 900)],
        "blacks": [(1300, 1100, 1900, 1600)],
    },
}


def ref_path(ref: str) -> Path:
    return PROCESS / f"referencias-{ref}.png"


def import_reference(src: Path, ref: str) -> Path:
    """La imagen bajada, a PNG en sRGB (sips convierte desde su perfil, P3 incluido). No la agranda."""
    out = ref_path(ref)
    subprocess.run(["sips", "-s", "format", "png", "--matchTo", SRGB_ICC, str(src), "--out", str(out)],
                   check=True, capture_output=True)
    return out


def load_reference(ref: str) -> np.ndarray:
    """Luz lineal float32 (h, w, 3)."""
    rgb = np.asarray(Image.open(ref_path(ref)).convert("RGB"), np.float32) / 255
    return srgb_to_linear(rgb)
