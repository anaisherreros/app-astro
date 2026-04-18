"""
Construcción del system prompt y del mensaje de usuario (context stuffing).
"""
from __future__ import annotations

import json
from typing import Any, Dict, Tuple

from .documents import (
    body_section_specs,
    load_interpretation_documents,
    system_prompt_filename,
)


def build_interpretation_prompt(
    chart_json: Dict[str, Any],
    documents: Dict[str, str] | None = None,
) -> Tuple[str, str]:
    """
    Devuelve (system_text, user_text) para la API de Anthropic.

    - system: contenido completo de system_prompt_atlas_astral.md
    - user: bloques [ ETIQUETA ] separados por --- más los datos de la carta en JSON.
    """
    docs = documents if documents is not None else load_interpretation_documents()
    sys_name = system_prompt_filename()
    system_text = docs[sys_name].strip()

    parts: list[str] = []
    for label, filename in body_section_specs():
        body = docs[filename].strip()
        parts.append(f"[ {label} ]\n\n{body}")

    user_core = "\n\n---\n\n".join(parts)
    chart_block = json.dumps(chart_json, ensure_ascii=False, indent=2)
    user_text = f"{user_core}\n\n---\n\nDatos de la carta:\n{chart_block}"

    return system_text, user_text
