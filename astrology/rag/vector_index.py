import json
import os
from typing import Dict, List, Tuple

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer


def _read_chunks_jsonl(chunks_path: str) -> List[Dict]:
    rows: List[Dict] = []
    with open(chunks_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def build_tfidf_index(chunks_path: str, index_path: str) -> Dict:
    rows = _read_chunks_jsonl(chunks_path)
    if not rows:
        raise ValueError(f"No chunks found in {chunks_path}")

    corpus = [row.get("text_index") or row.get("text") or "" for row in rows]
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        max_df=0.9,
        min_df=2,
    )
    matrix = vectorizer.fit_transform(corpus)

    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    payload = {
        "vectorizer": vectorizer,
        "matrix": matrix,
        "documents": rows,
    }
    joblib.dump(payload, index_path)

    return {
        "chunks_path": chunks_path,
        "index_path": index_path,
        "documents_count": len(rows),
        "features_count": len(vectorizer.get_feature_names_out()),
        "matrix_shape": [int(matrix.shape[0]), int(matrix.shape[1])],
    }

