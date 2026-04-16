from dataclasses import replace
from typing import List

from .schemas import Fact


LEVEL_BASE_SCORE = {
    "L1_NODO_NORTE": 100.0,
    "L2_CLAVES": 85.0,  # Sol, Luna, Saturno, Ascendente
    "L3_ROJOS": 65.0,  # Oposicion, Cuadratura
    "L4_AZULES": 45.0,  # Trigono, Sextil
    "L5_RESTO": 30.0,
}

KEY_BODIES = {"north_node", "sun", "moon", "saturn", "ascendant"}
L2_BODIES = {"sun", "moon", "saturn", "ascendant"}
RED_ASPECTS = {"opposition", "square"}
BLUE_ASPECTS = {"trine", "sextile"}


def _fact_level(fact: Fact) -> str:
    if fact.fact_type == "position":
        planet = fact.metadata.get("planet")
        if planet == "north_node":
            return "L1_NODO_NORTE"
        if planet in L2_BODIES:
            return "L2_CLAVES"
        return "L5_RESTO"

    if fact.fact_type == "aspect":
        aspect = fact.metadata.get("aspect")
        if aspect in RED_ASPECTS:
            return "L3_ROJOS"
        if aspect in BLUE_ASPECTS:
            return "L4_AZULES"
        return "L5_RESTO"

    return "L5_RESTO"


def _orb_bonus(fact: Fact) -> float:
    orb = fact.metadata.get("orb")
    if not isinstance(orb, (int, float)):
        return 0.0
    return max(0.0, 10.0 - float(orb))


def _key_body_bonus(fact: Fact) -> float:
    if fact.fact_type != "aspect":
        return 0.0
    a = fact.metadata.get("point_a")
    b = fact.metadata.get("point_b")
    if a in KEY_BODIES or b in KEY_BODIES:
        return 25.0
    return 0.0


def score_fact(fact: Fact) -> Fact:
    level = _fact_level(fact)
    score = LEVEL_BASE_SCORE[level]
    score += _orb_bonus(fact)
    score += _key_body_bonus(fact)
    return replace(fact, level=level, score=round(score, 2))


def score_facts(facts: List[Fact]) -> List[Fact]:
    scored = [score_fact(fact) for fact in facts]
    return sorted(scored, key=lambda item: item.score, reverse=True)

