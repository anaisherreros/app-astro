"""
Interpretación natal por LLM (MVP: context stuffing con documentos Markdown locales).
"""

from .chart_adapter import derive_figura_aspectos, normalize_chart_for_llm
from .readings import generate_astrology_reading

__all__ = [
    "derive_figura_aspectos",
    "generate_astrology_reading",
    "normalize_chart_for_llm",
]
