import os
from typing import Dict, List

import joblib
from sklearn.metrics.pairwise import linear_kernel

from .normalizer import normalize_text


DEFAULT_INDEX_PATH = os.path.join(
    "astrology",
    "rag",
    "data",
    "index",
    "tfidf_index.joblib",
)


def index_exists(index_path: str = DEFAULT_INDEX_PATH) -> bool:
    return os.path.exists(index_path)


class LocalTfidfRetriever:
    def __init__(self, index_path: str = DEFAULT_INDEX_PATH) -> None:
        if not os.path.exists(index_path):
            raise FileNotFoundError(
                f"TF-IDF index not found at {index_path}. Run: python -m astrology.rag.build_index"
            )
        payload = joblib.load(index_path)
        self.vectorizer = payload["vectorizer"]
        self.matrix = payload["matrix"]
        self.documents = payload["documents"]

    @staticmethod
    def _keyword_overlap_ratio(query: str, text_index: str) -> float:
        q_tokens = {tok for tok in normalize_text(query).split() if len(tok) > 2}
        d_tokens = {tok for tok in (text_index or "").split() if len(tok) > 2}
        if not q_tokens or not d_tokens:
            return 0.0
        return len(q_tokens & d_tokens) / len(q_tokens)

    def search(self, query: str, top_k: int = 4) -> List[Dict]:
        normalized_query = normalize_text(query)
        if not normalized_query:
            return []

        query_vector = self.vectorizer.transform([normalized_query])
        similarities = linear_kernel(query_vector, self.matrix).flatten()
        candidate_size = max(top_k * 8, top_k)
        candidate_indices = similarities.argsort()[::-1][:candidate_size]

        reranked = []
        for doc_idx in candidate_indices:
            doc = self.documents[int(doc_idx)]
            base_score = float(similarities[doc_idx])
            if base_score <= 0:
                continue
            overlap = self._keyword_overlap_ratio(query, doc.get("text_index", ""))
            final_score = (0.75 * base_score) + (0.25 * overlap)
            reranked.append((int(doc_idx), base_score, overlap, final_score))

        reranked.sort(key=lambda item: item[3], reverse=True)
        best = reranked[:top_k]

        hits: List[Dict] = []
        for rank, (doc_idx, base_score, overlap, final_score) in enumerate(best, start=1):
            doc = self.documents[int(doc_idx)]
            hits.append(
                {
                    "rank": rank,
                    "score": round(final_score, 6),
                    "score_tfidf": round(base_score, 6),
                    "score_overlap": round(overlap, 6),
                    "chunk_id": doc.get("chunk_id"),
                    "source_file": doc.get("source_file"),
                    "page_start": doc.get("page_start"),
                    "page_end": doc.get("page_end"),
                    "char_count": doc.get("char_count"),
                    "snippet": (doc.get("text") or "")[:380],
                }
            )
        return hits

