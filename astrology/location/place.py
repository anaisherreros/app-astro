import csv
import unicodedata
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo


CITIES_CSV_PATH = Path(__file__).resolve().parent / "cities_all.csv"


def _normalize_place(value):
    """
    Normaliza un texto para busquedas robustas:
    - minusculas
    - sin tildes
    - espacios compactados
    """
    normalized = unicodedata.normalize("NFKD", value)
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    normalized = normalized.lower().strip()
    normalized = " ".join(normalized.split())
    return normalized


@lru_cache(maxsize=1)
def _load_city_index():
    """
    Carga el CSV local de ciudades y crea un indice:
    query normalizada -> lista de candidatos.
    """
    if not CITIES_CSV_PATH.exists():
        raise FileNotFoundError(
            f"No se encontro el archivo de ciudades de prueba: {CITIES_CSV_PATH}"
        )

    city_index = {}
    with CITIES_CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            query = _normalize_place(row["query"])
            city_data = {
                "city": row["city"],
                "country_code": row["country_code"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "timezone": row["timezone"],
                "population": int(row.get("population", "0") or 0),
            }
            city_index.setdefault(query, []).append(city_data)

    # Si hay varias ciudades con el mismo nombre, priorizamos por mayor poblacion.
    for query in city_index:
        city_index[query].sort(key=lambda item: item["population"], reverse=True)

    return city_index


def _country_hint_from_input(key):
    """
    Extrae posible hint de pais desde inputs tipo:
    - "barcelona, es"
    - "lima, PE"
    """
    if "," not in key:
        return None
    parts = [part.strip() for part in key.split(",")]
    if len(parts) < 2:
        return None
    hint = parts[-1]
    if len(hint) == 2:
        return hint.upper()
    return None


def resolve_birth_place(birth_place):
    """
    Resuelve un lugar de nacimiento usando el CSV local.
    """
    if not birth_place:
        raise ValueError("birth_place es obligatorio.")

    city_index = _load_city_index()
    key = _normalize_place(birth_place)
    country_hint = _country_hint_from_input(key)

    # Si viene "ciudad, XX", usamos solo la parte de ciudad para buscar.
    city_key = key.split(",")[0].strip()

    # Coincidencia exacta por query normalizada.
    if city_key in city_index:
        candidates = city_index[city_key]

        # Si hay hint de pais, priorizamos ese candidato.
        if country_hint:
            for candidate in candidates:
                if candidate["country_code"].upper() == country_hint:
                    return candidate

        # Sin hint (o sin match de hint), devolvemos el mas poblado.
        return candidates[0]

    raise ValueError(
        f"No se encontro la ciudad '{birth_place}'. "
        "Prueba con formato 'ciudad, CC' (por ejemplo: 'valencia, ES')."
    )


def parse_birth_datetime(birth_date, birth_time):
    """
    Parsea fecha y hora de nacimiento en datetime local naive.
    """
    date_time_str = f"{birth_date} {birth_time}"
    try:
        return datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")


def to_utc_datetime(local_dt, timezone_name):
    """
    Convierte una fecha/hora local naive a UTC usando timezone IANA.
    """
    local_tz = ZoneInfo(timezone_name)
    aware_local_dt = local_dt.replace(tzinfo=local_tz)
    return aware_local_dt.astimezone(timezone.utc)


def resolve_birth_context(birth_date, birth_time, birth_place):
    """
    Orquesta la resolucion de lugar y conversion horaria:
    - city/country/lat/lon/timezone
    - local_dt y utc_dt
    """
    city_data = resolve_birth_place(birth_place)
    local_dt = parse_birth_datetime(birth_date, birth_time)
    utc_dt = to_utc_datetime(local_dt, city_data["timezone"])

    return {
        "city": city_data["city"],
        "country_code": city_data["country_code"],
        "latitude": city_data["latitude"],
        "longitude": city_data["longitude"],
        "timezone": city_data["timezone"],
        "local_dt": local_dt,
        "utc_dt": utc_dt,
    }


def search_city_suggestions(query, limit=12):
    """
    Devuelve sugerencias de ciudad para autocompletado.

    Estrategia:
    - prioriza coincidencias por prefijo
    - luego completa con coincidencias por inclusion
    - en cada query, la ciudad con mayor poblacion va primero
    """
    normalized_query = _normalize_place(query or "")
    if len(normalized_query) < 2:
        return []

    city_index = _load_city_index()
    startswith_hits = []
    contains_hits = []
    seen = set()

    def add_candidates(target, candidates):
        for city in candidates:
            dedupe_key = (city["city"], city["country_code"])
            if dedupe_key in seen:
                continue
            target.append(city)
            seen.add(dedupe_key)

    # 1) Recogemos todas las coincidencias por prefijo.
    for key, candidates in city_index.items():
        if key.startswith(normalized_query):
            add_candidates(startswith_hits, candidates)

    # 2) Recogemos coincidencias por inclusion solo si no se metieron antes.
    for key, candidates in city_index.items():
        if normalized_query in key and not key.startswith(normalized_query):
            add_candidates(contains_hits, candidates)

    # Priorizamos por poblacion dentro de cada grupo de matching.
    startswith_hits.sort(key=lambda item: item["population"], reverse=True)
    contains_hits.sort(key=lambda item: item["population"], reverse=True)

    ordered = startswith_hits + contains_hits

    suggestions = []
    for city in ordered[:limit]:
        suggestions.append(
            {
                "label": f'{city["city"]}, {city["country_code"]}',
                "value": f'{_normalize_place(city["city"])}, {city["country_code"]}',
                "city": city["city"],
                "country_code": city["country_code"],
                "timezone": city["timezone"],
            }
        )

    return suggestions

