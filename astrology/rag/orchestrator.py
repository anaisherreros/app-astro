from typing import Any, Dict

from .facts_builder import build_facts
from .query_builder import build_queries
from .retriever import LocalTfidfRetriever, index_exists
from .scoring import score_facts
from .selector import select_facts


def run_rag_prep(
    chart_result: Dict[str, Any],
    max_items: int = 18,
    min_red_aspects: int = 2,
    run_retrieval: bool = False,
    top_k: int = 4,
) -> Dict[str, Any]:
    """
    Prepara los artefactos base para RAG sin llamar al retriever ni al LLM.

    Devuelve:
    - hechos generados
    - hechos puntuados
    - hechos seleccionados
    - consultas de retrieval
    - reporte de cobertura
    """
    facts = build_facts(chart_result)
    scored_facts = score_facts(facts)
    selection = select_facts(
        scored_facts=scored_facts,
        max_items=max_items,
        min_red_aspects=min_red_aspects,
    )
    queries = build_queries(selection.selected_facts)
    retrieval_results = []
    retrieval_status = {
        "enabled": run_retrieval,
        "index_exists": index_exists(),
        "top_k": top_k,
    }

    if run_retrieval and retrieval_status["index_exists"]:
        retriever = LocalTfidfRetriever()
        retrieval_results = [
            {
                "query_id": query.query_id,
                "text_query": query.text_query,
                "source_fact_id": query.source_fact_id,
                "hits": retriever.search(query.text_query, top_k=top_k),
            }
            for query in queries
        ]

    return {
        "pipeline_status": {
            "current_step": 4 if retrieval_results else 3,
            "completed_steps": [1, 2, 3, 4] if retrieval_results else [1, 2, 3],
            "next_step": 5 if retrieval_results else 4,
            "step_name": (
                "retrieval_completed"
                if retrieval_results
                else "score_and_selection_ready_for_retrieval"
            ),
        },
        "facts_count": len(facts),
        "scored_facts": [fact.__dict__ for fact in scored_facts],
        "selected_facts": [fact.__dict__ for fact in selection.selected_facts],
        "overflow_facts": [fact.__dict__ for fact in selection.overflow_facts],
        "coverage_report": selection.coverage_report,
        "queries": [query.__dict__ for query in queries],
        "retrieval_status": retrieval_status,
        "retrieval_results": retrieval_results,
    }

