"""
Calculo de aspectos astrologicos.

Esta version calcula aspectos entre:
- Planetas (sun..pluto)
- Nodo Norte

Regla de orbes:
- Metodo Huber con prioridad por grupos.
- Se usa siempre el orbe del punto con mayor prioridad del par.
- Nodo Norte manda sobre todos.
"""

ASPECT_DEFINITIONS = [
    # Conjunto final pedido:
    # - Azules: sextil, trigono
    # - Verdes: semi sextil, quincuncio
    # - Rojos: cuadratura, oposicion
    # - Conjuncion
    {"name": "conjunction", "angle": 0, "kind": "neutral"},
    {"name": "sextile", "angle": 60, "kind": "blue"},
    {"name": "trine", "angle": 120, "kind": "blue"},
    {"name": "semi_sextile", "angle": 30, "kind": "green"},
    {"name": "quincunx", "angle": 150, "kind": "green"},
    {"name": "square", "angle": 90, "kind": "red"},
    {"name": "opposition", "angle": 180, "kind": "red"},
]

# Prioridad (de mayor a menor) para escoger tabla de orbes por pareja.
PRIORITY_ORDER = [
    "north_node",
    "personality_planets",
    "major_planets",
    "minor_planets",
]

# Mapeo de cada punto a su grupo de prioridad.
POINT_GROUP = {
    "north_node": "north_node",
    # Personality planets (pedido): Sun, Moon, Saturn
    "sun": "personality_planets",
    "moon": "personality_planets",
    "saturn": "personality_planets",
    # Major planets
    "jupiter": "major_planets",
    "uranus": "major_planets",
    "neptune": "major_planets",
    "pluto": "major_planets",
    # Minor planets
    "mercury": "minor_planets",
    "venus": "minor_planets",
    "mars": "minor_planets",
}

# Tabla de orbes por grupo y tipo de aspecto.
HUBER_ORBS = {
    "personality_planets": {
        "conjunction": 9.0,
        "opposition": 9.0,
        "trine": 8.0,
        "square": 7.0,
        "sextile": 5.0,
        "quincunx": 3.0,
        "semi_sextile": 2.0,
    },
    "major_planets": {
        "conjunction": 6.0,
        "opposition": 6.0,
        "trine": 5.0,
        "square": 4.0,
        "sextile": 3.0,
        "quincunx": 2.0,
        "semi_sextile": 1.5,
    },
    "minor_planets": {
        "conjunction": 5.0,
        "opposition": 5.0,
        "trine": 4.0,
        "square": 3.0,
        "sextile": 2.0,
        "quincunx": 1.5,
        "semi_sextile": 1.0,
    },
    "north_node": {
        "conjunction": 3.0,
        "opposition": 3.0,
        "trine": 2.0,
        "square": 2.0,
        "sextile": 1.5,
        "quincunx": 1.0,
        "semi_sextile": 1.0,
    },
}


def _angular_distance(longitude_a, longitude_b):
    """
    Distancia angular minima entre dos longitudes eclipticas.
    Siempre devuelve un valor entre 0 y 180.
    """
    delta = abs(longitude_a - longitude_b)
    if delta > 180:
        delta = 360 - delta
    return delta


def _point_group(point_name):
    """
    Devuelve el grupo de prioridad de un punto.
    Si no esta mapeado, se considera 'minor_planets' por defecto.
    """
    return POINT_GROUP.get(point_name, "minor_planets")


def _dominant_group(point_a, point_b):
    """
    Entre dos puntos, devuelve el grupo con mayor prioridad.
    """
    group_a = _point_group(point_a)
    group_b = _point_group(point_b)

    idx_a = PRIORITY_ORDER.index(group_a)
    idx_b = PRIORITY_ORDER.index(group_b)
    return group_a if idx_a < idx_b else group_b


def _allowed_orb_for_pair(point_a, point_b, aspect_name):
    """
    Orbe permitido para un aspecto concreto en una pareja concreta,
    aplicando la regla de prioridad Huber.
    """
    group = _dominant_group(point_a, point_b)
    return HUBER_ORBS[group][aspect_name], group


def _find_best_aspect(angle, point_a, point_b):
    """
    Busca el aspecto mas cercano al angulo dado segun orbes Huber.
    Devuelve None si no hay ningun aspecto dentro del orbe.
    """
    best_match = None

    # Comparamos contra cada aspecto ideal.
    for aspect in ASPECT_DEFINITIONS:
        aspect_name = aspect["name"]
        aspect_angle = aspect["angle"]
        aspect_kind = aspect["kind"]
        aspect_orb = abs(angle - aspect_angle)
        allowed_orb, priority_group = _allowed_orb_for_pair(
            point_a, point_b, aspect_name
        )

        # Regla estricta Huber: si se pasa del orbe, no existe aspecto.
        if aspect_orb <= allowed_orb:
            # Nos quedamos con el candidato de menor orbe (mas exacto).
            if best_match is None or aspect_orb < best_match["orb"]:
                best_match = {
                    "name": aspect_name,
                    "kind": aspect_kind,
                    "exact_angle": aspect_angle,
                    "orb": round(aspect_orb, 2),
                    "allowed_orb": allowed_orb,
                    "priority_group": priority_group,
                }

    return best_match


def _collect_points_for_aspects(planets, nodes):
    """
    Construye el mapa de puntos que participaran en aspectos.
    En esta fase: todos los planetas + nodo norte.
    """
    points = {}

    # 1) Planetas
    for planet_name, data in planets.items():
        points[planet_name] = data["longitude"]

    # 2) Nodo Norte (solo este nodo por ahora)
    points["north_node"] = nodes["north_node"]["longitude"]

    return points


def _collect_planet_names(planets):
    """
    Devuelve la lista de nombres de planetas para detectar inaspectados.
    """
    return list(planets.keys())


def calculate_aspects(planets, nodes):
    """
    Calcula aspectos entre planetas y nodo norte aplicando:
    - set visual de 7 aspectos
    - orbes Huber por prioridad
    - regla estricta de validacion por orbe

    Salida: lista de aspectos sin duplicados (A-B, pero no B-A).
    """
    points = _collect_points_for_aspects(planets, nodes)
    point_names = list(points.keys())
    aspects = []

    # Recorremos pares unicos: i < j evita duplicados y auto-aspectos.
    for i in range(len(point_names)):
        for j in range(i + 1, len(point_names)):
            point_a = point_names[i]
            point_b = point_names[j]

            lon_a = points[point_a]
            lon_b = points[point_b]

            # Paso 1: distancia angular real entre ambos puntos.
            angle = _angular_distance(lon_a, lon_b)

            # Paso 2: detectar si esa distancia cae en algun aspecto.
            aspect_match = _find_best_aspect(angle, point_a, point_b)
            if aspect_match is None:
                continue

            # Paso 3: guardar el aspecto detectado.
            aspects.append(
                {
                    "point_a": point_a,
                    "point_b": point_b,
                    "aspect": aspect_match["name"],
                    "kind": aspect_match["kind"],
                    "exact_angle": aspect_match["exact_angle"],
                    "angle": round(angle, 2),
                    "orb": aspect_match["orb"],
                    "allowed_orb": aspect_match["allowed_orb"],
                    "priority_group": aspect_match["priority_group"],
                }
            )

    # Orden opcional para lectura estable: primero por menor orbe.
    aspects.sort(key=lambda item: item["orb"])
    return aspects


def calculate_unaspected_planets(planets, aspects):
    """
    Detecta planetas inaspectados.

    Regla usada (pedido):
    - Si un planeta solo tiene conjunciones, sigue siendo inaspectado.
    - Necesita al menos un aspecto NO conjuncion para dejar de ser inaspectado.
    - Solo evaluamos planetas, no nodos.
    """
    planet_names = set(_collect_planet_names(planets))
    aspected_planets = set()

    for aspect in aspects:
        # La conjuncion no cuenta para "salir" de inaspectado.
        if aspect["aspect"] == "conjunction":
            continue

        point_a = aspect["point_a"]
        point_b = aspect["point_b"]

        if point_a in planet_names:
            aspected_planets.add(point_a)
        if point_b in planet_names:
            aspected_planets.add(point_b)

    unaspected = sorted(planet_names - aspected_planets)
    return unaspected


def calculate_major_aspects(planets, nodes, orb=6.0):
    """
    Alias de compatibilidad: conserva el nombre antiguo.
    `orb` se ignora porque ahora se usan orbes Huber por prioridad.
    """
    _ = orb
    all_aspects = calculate_aspects(planets, nodes)
    major_names = {"conjunction", "sextile", "square", "trine", "opposition"}
    return [item for item in all_aspects if item["aspect"] in major_names]

