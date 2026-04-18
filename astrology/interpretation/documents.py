"""
Carga de documentos Markdown para interpretación (context stuffing).
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

# Orden fijo del MVP (etiqueta legible, nombre de archivo)
_BODY_SPECS: List[Tuple[str, str]] = [
    ("JERARQUIA", "sistema_interpretativo_jerarquia_de_lectura.md"),
    ("PLANETAS", "sistema_interpretativo_planetas.md"),
    ("CASAS Y SIGNOS", "sistema_interpretativo_casas_y_signos.md"),
    ("NODO LUNAR", "sistema_interpretativo_nodo_lunar.md"),
    ("VOZ Y TONO", "sistema_interpretativo_voz_y_tono.md"),
]

_SYSTEM_FILENAME = "system_prompt_atlas_astral.md"


def markdown_dir() -> Path:
    """Directorio astrology/rag/data/markdown/ respecto al paquete astrology."""
    return Path(__file__).resolve().parent.parent / "rag" / "data" / "markdown"


def load_interpretation_documents(base: Path | None = None) -> Dict[str, str]:
    """
    Lee todos los .md necesarios y devuelve un dict nombre_archivo -> contenido UTF-8.
    Incluye system_prompt_atlas_astral.md y los cinco sistema_interpretativo_*.md del cuerpo.
    """
    root = base or markdown_dir()
    if not root.is_dir():
        raise FileNotFoundError(f"No existe el directorio de markdown: {root}")

    names = {_SYSTEM_FILENAME} | {fn for _, fn in _BODY_SPECS}
    out: Dict[str, str] = {}
    for filename in sorted(names):
        path = root / filename
        if not path.is_file():
            raise FileNotFoundError(f"Falta el documento requerido: {path}")
        out[filename] = path.read_text(encoding="utf-8")
    return out


def body_section_specs() -> List[Tuple[str, str]]:
    """(etiqueta, nombre_archivo) en el orden del prompt de usuario."""
    return list(_BODY_SPECS)


def system_prompt_filename() -> str:
    return _SYSTEM_FILENAME
