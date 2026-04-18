"""
Adapta la salida de calculate_chart al esquema del system prompt y deriva
figura_aspectos a partir del listado de aspectos (kind Huber: red/blue/green).
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Set

_PLANET_ES: Dict[str, str] = {
    "sun": "Sol",
    "moon": "Luna",
    "mercury": "Mercurio",
    "venus": "Venus",
    "mars": "Marte",
    "jupiter": "Júpiter",
    "saturn": "Saturno",
    "uranus": "Urano",
    "neptune": "Neptuno",
    "pluto": "Plutón",
}

_POINT_ES: Dict[str, str] = {
    **_PLANET_ES,
    "north_node": "Nodo Norte",
    "south_node": "Nodo Sur",
}

_ASPECT_ES: Dict[str, str] = {
    "conjunction": "conjunción",
    "opposition": "oposición",
    "square": "cuadratura",
    "trine": "trígono",
    "sextile": "sextil",
    "quincunx": "quincuncio",
    "semi_sextile": "semisextil",
}

_COLOR_ES: Dict[str, str] = {
    "red": "rojo",
    "blue": "azul",
    "green": "verde",
    "neutral": "neutro",
}

_SIGN_ELEMENT: Dict[str, str] = {
    "Aries": "fuego",
    "Leo": "fuego",
    "Sagitario": "fuego",
    "Tauro": "tierra",
    "Virgo": "tierra",
    "Capricornio": "tierra",
    "Géminis": "aire",
    "Libra": "aire",
    "Acuario": "aire",
    "Cáncer": "agua",
    "Escorpio": "agua",
    "Piscis": "agua",
}


def derive_figura_aspectos(aspects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Cuenta aspectos por color visual (kind). Conjunciones neutral no suman color.

    Heurística alineada con el material Huber del proyecto:
    - Predominio rojo -> lineal
    - Predominio azul -> triangular
    - Predominio verde -> cuadrangular
    - Empate rojo/azul cercano -> mixto + cuadrangular
    - Sin predominio claro -> mixto + mixta
    """
    r = b = g = 0
    for a in aspects:
        k = a.get("kind")
        if k == "red":
            r += 1
        elif k == "blue":
            b += 1
        elif k == "green":
            g += 1

    total = r + b + g
    conteo = {"rojo": r, "azul": b, "verde": g}

    if total == 0:
        return {
            "color_predominante": "mixto",
            "forma": "mixta",
            "conteo_por_color_visual": conteo,
            "nota": "Sin aspectos con color visual; figura indeterminada.",
        }

    sr, sb = r / total, b / total
    max_share = max(sr, sb, g / total)

    if r > 0 and b > 0 and abs(sr - sb) < 0.12 and max(sr, sb) >= 0.30:
        return {
            "color_predominante": "mixto",
            "forma": "cuadrangular",
            "conteo_por_color_visual": conteo,
        }

    if max_share < 0.36:
        return {
            "color_predominante": "mixto",
            "forma": "mixta",
            "conteo_por_color_visual": conteo,
        }

    if r >= b and r >= g and r > 0:
        return {
            "color_predominante": "rojo",
            "forma": "lineal",
            "conteo_por_color_visual": conteo,
        }
    if b >= r and b >= g and b > 0:
        return {
            "color_predominante": "azul",
            "forma": "triangular",
            "conteo_por_color_visual": conteo,
        }
    if g >= r and g >= b and g > 0:
        return {
            "color_predominante": "verde",
            "forma": "cuadrangular",
            "conteo_por_color_visual": conteo,
        }

    return {
        "color_predominante": "mixto",
        "forma": "mixta",
        "conteo_por_color_visual": conteo,
    }


def _point_label(name: str) -> str:
    return _POINT_ES.get(name, name.replace("_", " ").title())


def _element_counts(signs: List[str]) -> Dict[str, int]:
    counts = {"fuego": 0, "tierra": 0, "aire": 0, "agua": 0}
    for s in signs:
        el = _SIGN_ELEMENT.get(s)
        if el:
            counts[el] += 1
    return counts


def normalize_chart_for_llm(chart: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convierte el dict de calculate_chart al esquema del system prompt (español).

    Si ya trae 'planetas' y no 'planets', se asume normalizado y se devuelve copia.
    """
    if "planetas" in chart and "planets" not in chart:
        return deepcopy(chart)

    birth = chart.get("birth_data") or {}
    planets_raw: Dict[str, Any] = chart.get("planets") or {}
    nodes = chart.get("nodes") or {}
    angles = chart.get("angles") or {}
    aspects_raw: List[Dict[str, Any]] = list(chart.get("aspects") or [])
    unaspected: Set[str] = set(chart.get("unaspected_planets") or [])

    figura = derive_figura_aspectos(aspects_raw)

    planetas_list: List[Dict[str, Any]] = []
    element_signs: List[str] = []

    for key, label in _PLANET_ES.items():
        p = planets_raw.get(key)
        if not p:
            continue
        sign = p.get("sign", "")
        element_signs.append(sign)
        planetas_list.append(
            {
                "planeta": label,
                "signo": sign,
                "casa": p.get("house"),
                "grados": str(p.get("degree", "")),
                "inaspectado": key in unaspected,
            }
        )

    nn = nodes.get("north_node") or {}
    ns = nodes.get("south_node") or {}
    asc = angles.get("ascendant") or {}

    if nn.get("sign"):
        element_signs.append(nn["sign"])

    aspectos_out: List[Dict[str, Any]] = []
    for a in aspects_raw:
        aspectos_out.append(
            {
                "planeta1": _point_label(str(a.get("point_a", ""))),
                "planeta2": _point_label(str(a.get("point_b", ""))),
                "tipo": _ASPECT_ES.get(str(a.get("aspect", "")), str(a.get("aspect", ""))),
                "color": _COLOR_ES.get(str(a.get("kind", "")), str(a.get("kind", ""))),
                "orbe": a.get("orb"),
            }
        )

    elementos = _element_counts(element_signs)

    out: Dict[str, Any] = {
        "nombre": chart.get("nombre"),
        "fecha_nacimiento": birth.get("birth_date"),
        "hora_nacimiento": birth.get("birth_time"),
        "lugar_nacimiento": birth.get("birth_place"),
        "figura_aspectos": figura,
        "planetas": planetas_list,
        "nodo_norte": {
            "signo": nn.get("sign"),
            "casa": nn.get("house"),
            "grados": str(nn.get("degree", "")),
        },
        "nodo_sur": {
            "signo": ns.get("sign"),
            "casa": ns.get("house"),
            "grados": str(ns.get("degree", "")),
        },
        "ascendente": {
            "signo": asc.get("sign"),
            "grados": str(asc.get("degree", "")),
        },
        "aspectos": aspectos_out,
        "elementos": elementos,
    }

    mc = angles.get("mc") or {}
    if mc:
        out["medio_cielo"] = {
            "signo": mc.get("sign"),
            "grados": str(mc.get("degree", "")),
        }

    return out
