import unicodedata


PLANET_LABELS_ES = {
    "ascendant": "Ascendente",
    "sun": "Sol",
    "moon": "Luna",
    "mercury": "Mercurio",
    "venus": "Venus",
    "mars": "Marte",
    "jupiter": "Jupiter",
    "saturn": "Saturno",
    "uranus": "Urano",
    "neptune": "Neptuno",
    "pluto": "Pluton",
    "north_node": "Nodo Norte",
}


SIGN_DISPLAY_BY_CANONICAL = {
    "aries": "Aries",
    "tauro": "Tauro",
    "geminis": "Geminis",
    "cancer": "Cancer",
    "leo": "Leo",
    "virgo": "Virgo",
    "libra": "Libra",
    "escorpio": "Escorpio",
    "sagitario": "Sagitario",
    "capricornio": "Capricornio",
    "acuario": "Acuario",
    "piscis": "Piscis",
}


ASPECT_DISPLAY_BY_CANONICAL = {
    "conjunction": "conjuncion",
    "sextile": "sextil",
    "trine": "trigono",
    "semi_sextile": "semi sextil",
    "quincunx": "quincuncio",
    "square": "cuadratura",
    "opposition": "oposicion",
}

PLANET_QUERY_BY_KEY = {
    "ascendant": "ascendente",
    "sun": "sol",
    "moon": "luna",
    "mercury": "mercurio",
    "venus": "venus",
    "mars": "marte",
    "jupiter": "jupiter",
    "saturn": "saturno",
    "uranus": "urano",
    "neptune": "neptuno",
    "pluto": "pluton",
    "north_node": "nodo norte",
}


def normalize_text(value: str) -> str:
    if not isinstance(value, str):
        return ""
    normalized = unicodedata.normalize("NFD", value)
    normalized = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
    return normalized.lower().strip()


def normalize_sign(sign: str) -> str:
    normalized = normalize_text(sign)
    return normalized if normalized in SIGN_DISPLAY_BY_CANONICAL else "desconocido"


def sign_display(sign: str) -> str:
    canonical = normalize_sign(sign)
    if canonical == "desconocido":
        return sign or "--"
    return SIGN_DISPLAY_BY_CANONICAL[canonical]


def aspect_display(aspect: str) -> str:
    return ASPECT_DISPLAY_BY_CANONICAL.get(aspect, aspect)


def planet_display(planet_key: str) -> str:
    return PLANET_LABELS_ES.get(planet_key, planet_key)


def planet_query_label(planet_key: str) -> str:
    return PLANET_QUERY_BY_KEY.get(planet_key, planet_key)

