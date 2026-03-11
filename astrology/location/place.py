import csv
import unicodedata
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo


CITIES_CSV_PATH = Path(__file__).resolve().parent / "cities_test.csv"


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
    query normalizada -> datos de ciudad.
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
            city_index[query] = {
                "city": row["city"],
                "country_code": row["country_code"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "timezone": row["timezone"],
            }

    return city_index


def resolve_birth_place(birth_place):
    """
    Resuelve un lugar de nacimiento usando el CSV local.
    """
    if not birth_place:
        raise ValueError("birth_place es obligatorio.")

    city_index = _load_city_index()
    key = _normalize_place(birth_place)

    # Coincidencia exacta por query normalizada.
    if key in city_index:
        return city_index[key]

    # Fallback: contiene el query (ej: "Madrid, Spain").
    for query, city_data in city_index.items():
        if query in key:
            return city_data

    raise ValueError(
        f"No se encontro '{birth_place}' en cities_test.csv. "
        "Anade esa ciudad al archivo para poder calcular la carta."
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

