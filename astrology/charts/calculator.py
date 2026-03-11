# Paso 1: importar librerías necesarias
import swisseph as swe
from .aspects import calculate_aspects, calculate_unaspected_planets
from ..location.place import resolve_birth_context


def _longitude_to_sign(longitude):
    """
    Convierte longitud eclíptica (0-360°) en signo zodiacal y grados dentro del signo.
    Cada signo son 30°: 0-30 Aries, 30-60 Tauro, etc.
    """
    signs_es = [
        "Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
        "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis",
    ]
    # longitude % 360 por si acaso viene fuera de rango
    lon = longitude % 360.0
    sign_index = int(lon // 30)
    degree_in_sign = round(lon % 30, 2)
    return signs_es[sign_index], degree_in_sign


def _which_house(planet_longitude, cusps):
    """
    Determina en qué casa (1-12) está un planeta según las cúspides de casas.
    Asumimos que `cusps` tiene 12 elementos:
    cusps[0] = cúspide casa 1, ..., cusps[11] = cúspide casa 12.
    """
    lon = planet_longitude % 360.0
    n = len(cusps)  # normalmente 12

    for i in range(n):
        # i = 0 -> casa 1, i = 1 -> casa 2, ..., i = 11 -> casa 12
        start = cusps[i]
        end = cusps[(i + 1) % n]  # siguiente cúspide; para la última, vuelve a la primera

        if start <= end:
            # intervalo normal (no pasa por 360°)
            if start <= lon < end:
                return i + 1
        else:
            # intervalo que cruza 360° -> 0°
            if lon >= start or lon < end:
                return i + 1

    # Si por alguna razón no encaja en ningún intervalo, devolvemos casa 1
    return 1


def _planet_position(jd, cusps, body_id):
    """
    Calcula para un cuerpo (planeta o punto) su longitud, signo, grados y casa.
    body_id = constante de Swiss Ephemeris (swe.SUN, swe.MOON, etc.).
    """
    result = swe.calc_ut(jd, body_id)
    longitude = result[0][0]
    sign, degree = _longitude_to_sign(longitude)
    house = _which_house(longitude, cusps)
    return {
        "sign": sign,
        "degree": degree,
        "house": house,
        "longitude": round(longitude, 2),
    }


def calculate_chart(birth_date, birth_time, birth_place):
    """
    Calcula la carta natal usando Swiss Ephemeris.
    Recibe contexto ya resuelto de lugar/hora desde `location.place`.
    Calcula todos los planetas, nodos y ángulos (Ascendente, MC) en signo y casa.
    """

    # --- Paso 2: decirle a Swiss Ephemeris dónde buscar sus ficheros de datos ---
    swe.set_ephe_path(None)

    # --- Paso 3: resolver lugar, timezone y UTC en módulo dedicado ---
    birth_context = resolve_birth_context(birth_date, birth_time, birth_place)
    lat = birth_context["latitude"]
    lon = birth_context["longitude"]
    timezone_name = birth_context["timezone"]
    utc_dt = birth_context["utc_dt"]

    ut_hour = (
        utc_dt.hour
        + utc_dt.minute / 60.0
        + utc_dt.second / 3600.0
        + utc_dt.microsecond / 3_600_000_000.0
    )

    # --- Paso 6: día juliano UTC (lo que usa Swiss Ephemeris para todo) ---
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, ut_hour)

    # --- Paso 7: calcular cúspides de casas (Koch) y ángulos (ASC, MC) ---
    # ascmc[0] = Ascendente, ascmc[1] = MC (Medium Coeli), en longitud
    cusps, ascmc = swe.houses(jd, lat, lon, b"K")

    # --- Paso 8: planetas clásicos + Plutón (longitud → signo, grado, casa) ---
    planets = {
        "sun": _planet_position(jd, cusps, swe.SUN),
        "moon": _planet_position(jd, cusps, swe.MOON),
        "mercury": _planet_position(jd, cusps, swe.MERCURY),
        "venus": _planet_position(jd, cusps, swe.VENUS),
        "mars": _planet_position(jd, cusps, swe.MARS),
        "jupiter": _planet_position(jd, cusps, swe.JUPITER),
        "saturn": _planet_position(jd, cusps, swe.SATURN),
        "uranus": _planet_position(jd, cusps, swe.URANUS),
        "neptune": _planet_position(jd, cusps, swe.NEPTUNE),
        "pluto": _planet_position(jd, cusps, swe.PLUTO),
    }

    # --- Paso 9: Nodo Norte (medio). Nodo Sur = misma longitud + 180° ---
    north_result = swe.calc_ut(jd, swe.MEAN_NODE)
    north_lon = north_result[0][0]
    south_lon = (north_lon + 180.0) % 360.0
    north_sign, north_deg = _longitude_to_sign(north_lon)
    south_sign, south_deg = _longitude_to_sign(south_lon)
    nodes = {
        "north_node": {
            "sign": north_sign,
            "degree": north_deg,
            "house": _which_house(north_lon, cusps),
            "longitude": round(north_lon, 2),
        },
        "south_node": {
            "sign": south_sign,
            "degree": south_deg,
            "house": _which_house(south_lon, cusps),
            "longitude": round(south_lon, 2),
        },
    }

    # --- Paso 10: Ascendente y MC (vienen de swe.houses en ascmc) ---
    asc_lon = ascmc[0]
    mc_lon = ascmc[1]
    asc_sign, asc_deg = _longitude_to_sign(asc_lon)
    mc_sign, mc_deg = _longitude_to_sign(mc_lon)
    angles = {
        "ascendant": {"sign": asc_sign, "degree": asc_deg, "longitude": round(asc_lon, 2)},
        "mc": {"sign": mc_sign, "degree": mc_deg, "longitude": round(mc_lon, 2)},
    }

    # --- Paso 11: calcular aspectos (set visual: azul/verde/rojo + conjuncion) ---
    aspects = calculate_aspects(planets, nodes)
    unaspected_planets = calculate_unaspected_planets(planets, aspects)

    # --- Paso 12: devolver toda la carta calculada ---
    return {
        "birth_data": {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "birth_place": birth_place,
            "resolved_city": birth_context["city"],
            "resolved_country_code": birth_context["country_code"],
            "timezone_used": timezone_name,
            "latitude_used": lat,
            "longitude_used": lon,
        },
        "planets": planets,
        "nodes": nodes,
        "angles": angles,
        "aspects": aspects,
        "unaspected_planets": unaspected_planets,
    }
