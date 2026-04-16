import argparse
import json
import os

from .vector_index import build_tfidf_index


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build local TF-IDF vector index from chunks.jsonl"
    )
    parser.add_argument(
        "--chunks",
        default=os.path.join("astrology", "rag", "data", "chunks", "chunks.jsonl"),
        help="Input JSONL with chunked documents.",
    )
    parser.add_argument(
        "--index",
        default=os.path.join("astrology", "rag", "data", "index", "tfidf_index.joblib"),
        help="Output index path.",
    )
    args = parser.parse_args()

    summary = build_tfidf_index(chunks_path=args.chunks, index_path=args.index)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

