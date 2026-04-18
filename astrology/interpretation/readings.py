"""
Generación de interpretaciones completas (MVP: context stuffing + Claude).
"""
from __future__ import annotations

from typing import Any, Dict, Tuple

from .chart_adapter import normalize_chart_for_llm
from .claude_client import ClaudeUsage, call_claude_sonnet
from .prompt import build_interpretation_prompt


def generate_astrology_reading_with_usage(
    chart_json: Dict[str, Any],
) -> Tuple[str, ClaudeUsage]:
    """
    Igual que generate_astrology_reading pero devuelve también el uso de tokens.
    """
    payload = normalize_chart_for_llm(chart_json)
    system_text, user_text = build_interpretation_prompt(payload)
    return call_claude_sonnet(system_text, user_text)


def generate_astrology_reading(chart_json: Dict[str, Any]) -> str:
    """
    Carga documentos, construye prompt, llama a Claude Sonnet y devuelve el texto de la interpretación.

    Si chart_json es la salida de calculate_chart (planets, aspects, …), se normaliza al
    esquema del system prompt y se deriva figura_aspectos a partir de los aspectos.
    """
    interpretation, _usage = generate_astrology_reading_with_usage(chart_json)
    return interpretation
