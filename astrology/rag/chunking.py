import json
import os
import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


try:
    from pypdf import PdfReader
except ImportError as exc:  # pragma: no cover - runtime dependency check
    raise ImportError(
        "pypdf is required for PDF chunking. Install with: pip install pypdf"
    ) from exc


WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class ChunkConfig:
    chunk_size: int = 1200
    overlap: int = 180
    min_chunk_chars: int = 220
    skip_first_pages: int = 3
    max_digit_ratio: float = 0.25


def _normalize_spaces(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text or "").strip()


def _normalize_for_index(text: str) -> str:
    value = unicodedata.normalize("NFD", text)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    value = value.lower()
    return _normalize_spaces(value)


def _split_text(text: str, config: ChunkConfig) -> List[str]:
    clean = _normalize_spaces(text)
    if not clean:
        return []
    if len(clean) <= config.chunk_size:
        return [clean] if len(clean) >= config.min_chunk_chars else []

    chunks: List[str] = []
    start = 0
    step = max(1, config.chunk_size - config.overlap)

    while start < len(clean):
        end = min(start + config.chunk_size, len(clean))
        chunk = clean[start:end]
        if end < len(clean):
            split_pos = chunk.rfind(" ")
            if split_pos > config.chunk_size * 0.6:
                chunk = chunk[:split_pos]
                end = start + split_pos
        chunk = chunk.strip()
        if len(chunk) >= config.min_chunk_chars:
            chunks.append(chunk)
        if end >= len(clean):
            break
        start = max(start + step, end - config.overlap)

    return chunks


def _digit_ratio(text: str) -> float:
    if not text:
        return 1.0
    digits = sum(1 for c in text if c.isdigit())
    return digits / max(1, len(text))


def _looks_like_noise(chunk_text: str, config: ChunkConfig) -> bool:
    text = _normalize_spaces(chunk_text)
    lower = text.lower()

    noise_markers = [
        "isbn",
        "depósito legal",
        "deposito legal",
        "todos los derechos reservados",
        "índice",
        "indice",
        "prólogo",
        "prologo",
        "página",
        "pagina",
        "capítulo",
        "capitulo",
    ]
    if any(marker in lower for marker in noise_markers):
        return True

    # Demasiados digitos suele indicar indices/referencias editoriales.
    if _digit_ratio(text) > config.max_digit_ratio:
        return True

    # Si hay demasiados separadores visuales, suele ser poco util para retrieval.
    separators = text.count(".") + text.count("·") + text.count("|")
    if separators > 60:
        return True

    # Muy pocas palabras utiles.
    words = [w for w in re.split(r"\s+", lower) if w]
    unique_words = len(set(words))
    if unique_words < 25:
        return True

    return False


def _iter_pdf_files(pdf_dir: str) -> Iterable[str]:
    for name in sorted(os.listdir(pdf_dir)):
        if name.lower().endswith(".pdf"):
            yield os.path.join(pdf_dir, name)


def _extract_chunks_from_pdf(pdf_path: str, config: ChunkConfig) -> Tuple[List[Dict], Dict]:
    reader = PdfReader(pdf_path)
    source_file = os.path.basename(pdf_path)
    source_title = os.path.splitext(source_file)[0]
    chunk_rows: List[Dict] = []
    page_count = len(reader.pages)

    skipped_by_page = 0
    skipped_by_noise = 0

    for idx, page in enumerate(reader.pages):
        page_num = idx + 1
        if page_num <= config.skip_first_pages:
            skipped_by_page += 1
            continue
        text = _normalize_spaces(page.extract_text() or "")
        if not text:
            continue
        page_chunks = _split_text(text, config)
        for local_idx, chunk_text in enumerate(page_chunks, start=1):
            if _looks_like_noise(chunk_text, config):
                skipped_by_noise += 1
                continue
            chunk_id = f"{source_title}__p{page_num:03d}__c{local_idx:02d}"
            row = {
                "chunk_id": chunk_id,
                "source_file": source_file,
                "source_title": source_title,
                "page_start": page_num,
                "page_end": page_num,
                "text": chunk_text,
                "text_index": _normalize_for_index(chunk_text),
                "char_count": len(chunk_text),
            }
            chunk_rows.append(row)

    stats = {
        "source_file": source_file,
        "source_title": source_title,
        "page_count": page_count,
        "chunk_count": len(chunk_rows),
        "skipped_first_pages": skipped_by_page,
        "skipped_noise_chunks": skipped_by_noise,
    }
    return chunk_rows, stats


def build_chunks(
    pdf_dir: str,
    output_jsonl: str,
    stats_json: str,
    config: ChunkConfig | None = None,
) -> Dict:
    cfg = config or ChunkConfig()
    os.makedirs(os.path.dirname(output_jsonl), exist_ok=True)
    os.makedirs(os.path.dirname(stats_json), exist_ok=True)

    all_chunks: List[Dict] = []
    source_stats: List[Dict] = []

    for pdf_path in _iter_pdf_files(pdf_dir):
        rows, stats = _extract_chunks_from_pdf(pdf_path, cfg)
        all_chunks.extend(rows)
        source_stats.append(stats)

    with open(output_jsonl, "w", encoding="utf-8") as fh:
        for row in all_chunks:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = {
        "pdf_dir": pdf_dir,
        "output_jsonl": output_jsonl,
        "chunk_config": {
            "chunk_size": cfg.chunk_size,
            "overlap": cfg.overlap,
            "min_chunk_chars": cfg.min_chunk_chars,
            "skip_first_pages": cfg.skip_first_pages,
            "max_digit_ratio": cfg.max_digit_ratio,
        },
        "total_sources": len(source_stats),
        "total_chunks": len(all_chunks),
        "sources": source_stats,
    }

    with open(stats_json, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)

    return summary

