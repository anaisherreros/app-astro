from ..charts.calculator import calculate_chart
from ..rag.orchestrator import run_rag_prep

def get_chart_info(birth_date, birth_time, birth_place):

    if not birth_date or not birth_time or not birth_place:
        return {
            "error": "Missing required data",
            "required": ["birth_date", "birth_time", "birth_place"]
        }

    chart_data = calculate_chart(birth_date, birth_time, birth_place)
    rag_preview = run_rag_prep(chart_data, run_retrieval=True, top_k=4)

    return {
        "message": "Chart calculated successfully",
        "result": chart_data,
        "rag_preview": rag_preview,
    }