import argparse
import json
import os

try:
    from .chunking import ChunkConfig, build_chunks
except ImportError:  # pragma: no cover
    from chunking import ChunkConfig, build_chunks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build initial RAG chunks from PDF files."
    )
    parser.add_argument(
        "--pdf-dir",
        default=os.path.join("astrology", "rag", "data", "pdf"),
        help="Directory containing source PDF files.",
    )
    parser.add_argument(
        "--output",
        default=os.path.join("astrology", "rag", "data", "chunks", "chunks.jsonl"),
        help="Output JSONL path for chunks.",
    )
    parser.add_argument(
        "--stats",
        default=os.path.join("astrology", "rag", "data", "chunks", "stats.json"),
        help="Output JSON path for chunking statistics.",
    )
    parser.add_argument("--chunk-size", type=int, default=1200)
    parser.add_argument("--overlap", type=int, default=180)
    parser.add_argument("--min-chars", type=int, default=220)
    parser.add_argument("--skip-first-pages", type=int, default=3)
    parser.add_argument("--max-digit-ratio", type=float, default=0.25)
    args = parser.parse_args()

    summary = build_chunks(
        pdf_dir=args.pdf_dir,
        output_jsonl=args.output,
        stats_json=args.stats,
        config=ChunkConfig(
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            min_chunk_chars=args.min_chars,
            skip_first_pages=args.skip_first_pages,
            max_digit_ratio=args.max_digit_ratio,
        ),
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

