"""
Llamada a Claude (Anthropic Messages API).
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Tuple

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
DEFAULT_MAX_TOKENS = int(os.environ.get("ANTHROPIC_MAX_TOKENS", "16384"))


@dataclass(frozen=True)
class ClaudeUsage:
    input_tokens: int
    output_tokens: int


def call_claude_sonnet(
    system_prompt: str,
    user_message: str,
    *,
    model: str | None = None,
    max_tokens: int | None = None,
    api_key: str | None = None,
) -> Tuple[str, ClaudeUsage]:
    """
    Envía system + un único mensaje user. Imprime uso de tokens en stdout (MVP).
    Devuelve (texto de la interpretación, uso).
    """
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        logger.error("call_claude_sonnet: ANTHROPIC_API_KEY no definida")
        raise ValueError(
            "Falta ANTHROPIC_API_KEY en el entorno (o pasa api_key=...)."
        )

    import anthropic

    client = anthropic.Anthropic(api_key=key)
    use_model = model or DEFAULT_MODEL
    use_max = max_tokens if max_tokens is not None else DEFAULT_MAX_TOKENS

    logger.info(
        "call_claude_sonnet: peticion Anthropic (model=%s max_tokens=%s)",
        use_model,
        use_max,
    )

    message = client.messages.create(
        model=use_model,
        max_tokens=use_max,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    usage = ClaudeUsage(
        input_tokens=message.usage.input_tokens,
        output_tokens=message.usage.output_tokens,
    )
    logger.info(
        "Claude usage: input_tokens=%s output_tokens=%s",
        usage.input_tokens,
        usage.output_tokens,
    )

    text_parts: list[str] = []
    block_types: list[str] = []
    for block in message.content:
        btype = getattr(block, "type", None)
        if btype is None and isinstance(block, dict):
            btype = block.get("type")
        block_types.append(str(btype))
        if btype == "text":
            chunk = getattr(block, "text", None)
            if chunk is None and isinstance(block, dict):
                chunk = block.get("text")
            if chunk:
                text_parts.append(str(chunk))

    text = "".join(text_parts).strip()
    if not text:
        logger.warning(
            "call_claude_sonnet: respuesta sin bloques de texto (tipos=%s)",
            block_types,
        )
    return text, usage
