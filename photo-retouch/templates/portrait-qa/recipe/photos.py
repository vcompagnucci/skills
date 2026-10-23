"""Datos de cada foto, medidos a ojo sobre la imagen revelada. Pixeles de la imagen completa.

- crop: recorte cuadrado para foto de perfil (x0, y0, lado). La cabeza ocupa ~la
  mitad del lado y sobra aire hacia donde mira. Es el encuadre "medio", el de las
  referencias.
- wide: encuadre "abierto", todo el ancho de la foto: torso y manos.
- features: ojos, boca y fosas nasales (cx, cy, rx, ry). El retoque de piel no los
  toca: sin esto, emparejar el rojo desaturaba los labios.
- skin_ev: dodge sobre la piel (pincel suave que sigue la piel, no un disco), en EV.
  Solo para una cara ~3 EV en sombra respecto de la ropa: sin separarlas, la campera
  negra sale gris cuando la cara llega a su brillo. Sin la clave, no hay dodge.
- face: centro y radio de la cara (cx, cy, r), para luz local y brillos.
- spots: granos y marcas rojas a curar (x, y, radio), revisados ampliados.
- freckles: pecas y lunares que se dejan a proposito; quedan anotados para no
  curarlos por error en una pasada futura.
- hot: pixeles calientes del sensor (x, y): se cambian por la mediana de sus vecinos.
- wall_keys: pared que el matte toma por persona (x, y, medio lado, x e y de una muestra
  de pared): ahi el alpha se corrige por distancia al color de la pared.

Abajo, UN ejemplo inventado con todas las claves: hay que reemplazarlo por las fotos de la sesion,
medidas a mano sobre el revelado. Las claves son el nombre del archivo en originales/ sin extension.
"""

PHOTOS = {
    "PHOTO_A": {
        # ojo derecho, ojo izquierdo, boca, fosas nasales (cx, cy, rx, ry)
        "features": [(1560, 1860, 60, 34), (1780, 1845, 80, 40), (1650, 2180, 130, 50), (1650, 2060, 70, 28)],
        "crop": (400, 880, 2500),
        "wide": (0, 880, 4170),
        "face": (1720, 1960, 430),
        "skin_ev": 1.5,
        "spots": [
            (1840, 2000, 9),
            (1690, 2320, 7),
            (1650, 1730, 6),  # grano junto a la ceja
        ],
        # pixeles calientes del sensor (x, y)
        "hot": [(2240, 4120)],
        # pared que el matte toma por persona: (x, y, medio lado de la zona, x e y de una
        # muestra de pared). El hueco entre el brazo y la mano, por ejemplo.
        "wall_keys": [(2640, 5000, 70, 2650, 5020)],
        "freckles": [
            (1880, 1960, 7),
            (1815, 1930, 6),
        ],
    },
}
