from typing import Dict, List, Set

from .schemas import Fact, SelectionResult


MANDATORY_POSITION_BODIES = {"north_node", "sun", "moon", "saturn", "ascendant"}
RED_ASPECTS = {"opposition", "square"}


def _position_by_planet(facts: List[Fact], planet: str) -> List[Fact]:
    return [
        fact
        for fact in facts
        if fact.fact_type == "position" and fact.metadata.get("planet") == planet
    ]


def _red_aspects(facts: List[Fact]) -> List[Fact]:
    return [
        fact
        for fact in facts
        if fact.fact_type == "aspect" and fact.metadata.get("aspect") in RED_ASPECTS
    ]


def select_facts(
    scored_facts: List[Fact],
    max_items: int = 18,
    min_red_aspects: int = 2,
) -> SelectionResult:
    selected: List[Fact] = []
    selected_ids: Set[str] = set()

    def add_fact(fact: Fact) -> None:
        if fact.fact_id in selected_ids:
            return
        if len(selected) >= max_items:
            return
        selected.append(fact)
        selected_ids.add(fact.fact_id)

    # 1) Cobertura minima obligatoria de posiciones clave.
    for body in ("north_node", "sun", "moon", "saturn", "ascendant"):
        for fact in _position_by_planet(scored_facts, body):
            add_fact(fact)

    # 2) Aspectos rojos obligatorios (si existen).
    red_added = 0
    for fact in _red_aspects(scored_facts):
        if red_added >= min_red_aspects:
            break
        previous_len = len(selected)
        add_fact(fact)
        if len(selected) > previous_len:
            red_added += 1

    # 3) Completar por score hasta max_items.
    for fact in scored_facts:
        add_fact(fact)
        if len(selected) >= max_items:
            break

    overflow = [fact for fact in scored_facts if fact.fact_id not in selected_ids]

    covered_positions = {
        body: any(
            f.fact_type == "position" and f.metadata.get("planet") == body
            for f in selected
        )
        for body in MANDATORY_POSITION_BODIES
    }
    covered_red_aspects = sum(
        1
        for f in selected
        if f.fact_type == "aspect" and f.metadata.get("aspect") in RED_ASPECTS
    )

    missing: List[str] = []
    for body, covered in covered_positions.items():
        if not covered:
            missing.append(f"position:{body}")
    if covered_red_aspects < min_red_aspects:
        missing.append(f"red_aspects_min:{min_red_aspects}")

    coverage_report: Dict[str, object] = {
        "required_positions": sorted(MANDATORY_POSITION_BODIES),
        "covered_positions": covered_positions,
        "required_min_red_aspects": min_red_aspects,
        "covered_red_aspects": covered_red_aspects,
        "is_complete": len(missing) == 0,
        "missing": missing,
        "selected_count": len(selected),
        "overflow_count": len(overflow),
    }

    return SelectionResult(
        selected_facts=selected,
        overflow_facts=overflow,
        coverage_report=coverage_report,
    )

