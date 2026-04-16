from typing import Any, Dict, List, Set, Tuple

from .normalizer import aspect_display, normalize_sign, planet_display, sign_display
from .schemas import Fact


PLANET_ORDER = [
    "ascendant",
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "north_node",
]


def _planet_entry(chart_result: Dict[str, Any], key: str) -> Dict[str, Any]:
    if key == "ascendant":
        return chart_result.get("angles", {}).get("ascendant") or {}
    if key == "north_node":
        return chart_result.get("nodes", {}).get("north_node") or {}
    return chart_result.get("planets", {}).get(key) or {}


def _build_position_fact(key: str, data: Dict[str, Any]) -> Fact:
    sign_raw = data.get("sign", "")
    sign_key = normalize_sign(sign_raw)
    sign_text = sign_display(sign_raw)
    house = data.get("house")
    degree = data.get("degree")

    fact_id = f"{key}_in_{sign_key}_house_{house if house is not None else 'na'}"
    text = (
        f"{planet_display(key)} en {sign_text} en casa {house if house is not None else '--'}"
        f"{f' ({degree}°)' if isinstance(degree, (int, float)) else ''}."
    )

    return Fact(
        fact_id=fact_id,
        fact_type="position",
        text_display=text,
        metadata={
            "planet": key,
            "sign": sign_key,
            "house": house,
            "degree": degree,
        },
    )


def _canonical_aspect_pair(point_a: str, point_b: str) -> Tuple[str, str]:
    left, right = sorted([point_a, point_b])
    return left, right


def _build_aspect_fact(item: Dict[str, Any]) -> Fact:
    point_a = item.get("point_a", "")
    point_b = item.get("point_b", "")
    aspect = item.get("aspect", "")
    orb = item.get("orb")

    left, right = _canonical_aspect_pair(point_a, point_b)
    fact_id = f"{left}_{aspect}_{right}"
    text = (
        f"{planet_display(point_a)} en {aspect_display(aspect)} con {planet_display(point_b)}"
        f"{f' (orbe {orb}°)' if isinstance(orb, (int, float)) else ''}."
    )

    return Fact(
        fact_id=fact_id,
        fact_type="aspect",
        text_display=text,
        metadata={
            "point_a": point_a,
            "point_b": point_b,
            "aspect": aspect,
            "orb": orb,
            "pair_canonical": [left, right],
        },
    )


def _build_unaspected_fact(chart_result: Dict[str, Any], key: str) -> Fact:
    data = chart_result.get("planets", {}).get(key) or {}
    sign_raw = data.get("sign", "")
    house = data.get("house")
    sign_key = normalize_sign(sign_raw)
    sign_text = sign_display(sign_raw)
    fact_id = f"{key}_unaspected"
    text = f"{planet_display(key)} inaspectado en {sign_text} en casa {house if house is not None else '--'}."

    return Fact(
        fact_id=fact_id,
        fact_type="unaspected",
        text_display=text,
        metadata={
            "planet": key,
            "sign": sign_key,
            "house": house,
        },
    )


def build_facts(chart_result: Dict[str, Any]) -> List[Fact]:
    facts: List[Fact] = []

    for key in PLANET_ORDER:
        entry = _planet_entry(chart_result, key)
        if entry:
            facts.append(_build_position_fact(key, entry))

    seen_aspects: Set[str] = set()
    for aspect_item in chart_result.get("aspects", []) or []:
        aspect_fact = _build_aspect_fact(aspect_item)
        if aspect_fact.fact_id in seen_aspects:
            continue
        seen_aspects.add(aspect_fact.fact_id)
        facts.append(aspect_fact)

    for planet_key in chart_result.get("unaspected_planets", []) or []:
        facts.append(_build_unaspected_fact(chart_result, planet_key))

    return facts


def build_facts_debug(chart_result: Dict[str, Any]) -> Dict[str, Any]:
    facts = build_facts(chart_result)
    return {
        "count": len(facts),
        "positions": [f.__dict__ for f in facts if f.fact_type == "position"],
        "aspects": [f.__dict__ for f in facts if f.fact_type == "aspect"],
        "unaspected": [f.__dict__ for f in facts if f.fact_type == "unaspected"],
        "all": [f.__dict__ for f in facts],
    }

