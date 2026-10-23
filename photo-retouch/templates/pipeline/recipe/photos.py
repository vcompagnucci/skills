"""Datos de cada foto, medidos sobre el revelado. Pixeles de la imagen completa (6246 x 4170
o 4170 x 6246, ya rotada), salvo `wall`, que va en fracciones del alto y el ancho.

- wall: parches de pared para el balance de blancos (y0, y1, x0, x1 en fracciones).
- blacks: recuadros de ropa negra con luz pareja (x0, y0, x1, y1 en pixeles), para medir el negro
  contra las referencias de estilo (tools/ref_measure.py).
- faces: una entrada por cara. `oval` (cx, cy, rx, ry) limita el retoque de piel;
  `features` son elipses (cx, cy, rx, ry[, angulo]) de ojos, cejas, boca y fosas nasales,
  que el retoque no toca. Los dos primeros son siempre los ojos.
- lids: la linea de pestanas de abajo de cada ojo (tres puntos, en el orden de los ojos de
  `features`), donde empieza la correccion de ojeras. Leida en proceso/31-ojeras.
- backdrop_holes: pared encerrada por la gente que la mascara de los estilos no encuentra sola
  (x0, y0, x1, y1 en pixeles): adentro, lo que tiene color de pared es pared, y el matting decide
  el borde. Leidos en proceso/estilos-huecos-piloto-<foto>.png (tools/backdrop_holes.py).
- backdrop_sure: lo mismo, pero el recuadro decide los dos lados: lo que tiene color de pared es pared
  segura aunque este junto a una cabeza (ahi la regla automatica no busca), y lo negro y macizo es persona
  segura. Para pared en sombra entre ropa negra y pelo, donde el matting solo no separa. No sirve si en el
  recuadro hay algo gris neutro que no es pared (el puno gris de una manga se aclaraba). Los
  pelos que cruzan la pared los devuelve key_thin_hair.
- backdrop_keep: persona segura, poligonos de (x, y) en pixeles: lo que la regla automatica llama pared y es
  gente (el cuero blanco de una zapatilla en sombra tiene el gris de la pared). Adentro el alpha es 1 y el
  matting decide el borde contra la pared de afuera, asi que el poligono va 2 px adentro del borde. Leidos en
  proceso/estilos-alpha-rojo-<foto>.png (tools/backdrop_alpha_red.py) y trazados sobre la luz: el cuero en
  sombra (25-36 L*) contra la pared (40-58).

- spots / kept / hot: granos y marcas a curar (x, y, radio), lo que se deja a proposito (pecas, lunares: anotado
  para no curarlo por error en otra pasada) y pixeles calientes del sensor (x, y).
- wall_marks: manchas de la pared a curar (x, y, radio), leidas en proceso/21-pared. lint_keep: recuadros
  (x, y, ancho, alto) que la busqueda de pelusas no toca (un raspon del banco no es ropa).
- faces[].id: una etiqueta libre por persona, la misma en todas las fotos donde aparece (asi copiar las ojeras
  de un retrato a la de grupo cae en la misma cara). El editor la muestra con FACE_NAMES de
  viewer_template.html, o capitalizada si no esta ahi. under_eye ajusta la correccion de ojeras de esa cara
  (recipe/undereye.py); teeth marca una sonrisa con dientes, que el retoque de piel no toca.

Abajo, UN ejemplo inventado con todas las claves: hay que reemplazarlo por las fotos de la sesion, medidas a mano
sobre el revelado (tools/grid.py, tools/check_faces.py, proceso/31-ojeras). Las claves son el nombre del archivo
en originales/ sin extension.
"""

PHOTOS = {
    "PHOTO_A": {
        "wall": [(0.02, 0.10, 0.03, 0.20), (0.02, 0.10, 0.75, 0.95)],
        # pared encerrada por la gente que la regla automatica no encuentra (un hueco entre un brazo y el cuerpo)
        "backdrop_holes": [(3400, 3800, 3450, 3880)],
        # pared en sombra entre el pelo y una remera negra, adentro de la elipse de la cabeza: el recuadro decide
        "backdrop_sure": [(2380, 2600, 2560, 3040)],
        # una zapatilla blanca en sombra con el gris de la pared: persona segura, el poligono 2 px adentro del borde
        "backdrop_keep": [[(1480, 5500), (1700, 5500), (1780, 5600), (1790, 5800), (1840, 6050), (1880, 6070),
                           (1880, 6246), (1480, 6246)]],
        "blacks": [(700, 2300, 1100, 2900), (2900, 2900, 3300, 3500)],  # ropa negra con luz pareja (x0, y0, x1, y1): el negro de la medida de estilos
        # granos y marcas rojas (x, y, radio): uno en el menton y dos puntos rojos de una mejilla
        "spots": [(1650, 2870, 6), (2690, 1780, 5), (2720, 1830, 5)],
        "kept": [(2740, 1820, 3)],  # una peca: queda
        "hot": [(3020, 2060)],  # un pixel caliente del sensor
        # manchas de la pared (x, y, radio), leidas en proceso/21-pared: puntos sueltos y una arruga (claro y oscuro
        # lado a lado: tres puntos a lo largo). Las costuras del papel no son manchas y quedan.
        "wall_marks": [
            (890, 5930, 8),
            (900, 5940, 16),  # la sombra ancha alrededor del punto anterior
            (3930, 420, 11),
            (3935, 434, 11),
            (3940, 448, 11),
        ],
        # pelusas: el raspon claro de la pata del banco no es ropa, queda
        "lint_keep": [(1300, 6070, 40, 40)],
        "faces": [
            {
                "id": "persona-1",
                "lids": [[(1190, 1250), (1240, 1255), (1290, 1248)], [(1400, 1260), (1450, 1268), (1495, 1272)]],
                "oval": (1360, 1280, 250, 330),
                "features": [
                    (1243, 1234, 58, 22),  # ojo derecho
                    (1452, 1254, 58, 22, 5),  # ojo izquierdo
                    (1238, 1167, 85, 24, -3),  # ceja derecha
                    (1465, 1186, 85, 24, 10),  # ceja izquierda
                    (1338, 1362, 62, 20),  # fosas nasales
                    (1356, 1462, 110, 32),  # boca
                ],
            },
            {
                "id": "persona-2",
                "lids": [[(2730, 1780), (2765, 1786), (2810, 1778)], [(2935, 1768), (2970, 1774), (3010, 1770)]],
                # la ojera esta del lado del lagrimal, pegada a las pestanas; el ojo de atras va en sombra
                "under_eye": {"depth": 0.75, "span": 0.66, "shift": 0.15, "reach_lashes": True, "eyes": [{}, {"light": 0.3, "color": 0.4}]},
                "teeth": True,  # sonrie con los dientes a la vista
                "oval": (2880, 1880, 240, 320),
                "features": [
                    (2770, 1765, 58, 22),
                    (2965, 1758, 58, 22),
                    (2760, 1710, 85, 20, 3),
                    (2990, 1705, 75, 20, -3),
                    (2875, 1880, 55, 18),
                    (2875, 1985, 95, 35),
                ],
            },
        ],
    },
}

# Las de la sesion, con sus datos a mano. Los pasos que dependen de esos datos (estilos, mediciones) recorren
# estas, no las importadas
STUDIO = tuple(PHOTOS)


# Las fotos que se suman desde el editor (+ en la barra de fotos, recipe/import_photo.py): sin datos a mano, solo lo que
# se mide solo. `faces` sale del detector de caras de macOS (solo ubica: nada se genera) y alcanza para el matting del
# fondo; sin `features` ni `lids` no hay retoque de piel ni ojeras hasta que se inventarien a ojo, como las de la sesion.
# El registro lo escribe el servidor; las pruebas lo apuntan a una copia (EDITOR_IMPORTS), como EDITOR_VERSIONS.
def _imports_path():
    import os
    from pathlib import Path

    return Path(os.environ.get("EDITOR_IMPORTS") or Path(__file__).resolve().parent.parent / "editadas" / "importadas.json")


def load_imports() -> dict:
    import json

    path = _imports_path()
    try:
        return json.loads(path.read_text())["photos"] if path.exists() else {}
    except (OSError, ValueError, KeyError):
        return {}


IMPORTS = _imports_path()
PHOTOS.update({k: v for k, v in load_imports().items() if k not in STUDIO})
