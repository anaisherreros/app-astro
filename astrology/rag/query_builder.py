from typing import List

from .normalizer import aspect_display, planet_query_label
from .schemas import Fact, RetrievalQuery


ASPECT_QUERY_EXPANSION = {
    "square": ["desafio", "tension", "bloqueo"],
    "opposition": ["polaridad", "conflicto", "equilibrio"],
    "trine": ["talento", "fluidez", "armonico"],
    "sextile": ["talento", "oportunidad", "cooperacion"],
    "conjunction": ["fusion", "enfoque", "intensidad"],
    "quincunx": ["ajuste", "adaptacion", "incomodidad"],
    "semi_sextile": ["aprendizaje", "integracion", "progreso"],
}


def _query_from_fact(fact: Fact) -> str:
    if fact.fact_type == "position":
        planet = fact.metadata.get("planet")
        sign = fact.metadata.get("sign")
        house = fact.metadata.get("house")
        return f"{planet_query_label(planet)} en {sign} casa {house} interpretacion astrologica"

    if fact.fact_type == "aspect":
        a = fact.metadata.get("point_a")
        b = fact.metadata.get("point_b")
        aspect = fact.metadata.get("aspect")
        extras = " ".join(ASPECT_QUERY_EXPANSION.get(aspect, []))
        return (
            f"{planet_query_label(a)} en {aspect_display(aspect)} con "
            f"{planet_query_label(b)} interpretacion astrologica {extras}"
        )

    if fact.fact_type == "unaspected":
        planet = fact.metadata.get("planet")
        return f"{planet_query_label(planet)} inaspectado interpretacion astrologica"

    return fact.text_display


def build_queries(selected_facts: List[Fact]) -> List[RetrievalQuery]:
    queries: List[RetrievalQuery] = []
    for idx, fact in enumerate(selected_facts, start=1):
        queries.append(
            RetrievalQuery(
                query_id=f"q_{idx}",
                text_query=_query_from_fact(fact),
                source_fact_id=fact.fact_id,
                score=fact.score,
            )
        )
    return queries

