"""
EduPath AI - BM25 Keyword Search
Provides BM25 keyword-based retrieval using rank_bm25.
"""

from typing import List, Dict, Any, Optional
import re
from rank_bm25 import BM25Okapi

def tokenize(text: str) -> List[str]:
    """Simple alphanumeric tokenizer for BM25 indexing."""
    if not text:
        return []
    return re.findall(r"\w+", text.lower())

class BM25SearchEngine:
    def __init__(self):
        self.corpus_chunks: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25: Optional[BM25Okapi] = None

    def build_index(self, chunks: List[Dict[str, Any]]) -> None:
        """Build or rebuild BM25 index from a list of chunks."""
        self.corpus_chunks = chunks
        self.tokenized_corpus = [tokenize(c["text"]) for c in chunks]
        if self.tokenized_corpus and any(self.tokenized_corpus):
            self.bm25 = BM25Okapi(self.tokenized_corpus)
        else:
            self.bm25 = None

    def search(
        self,
        query: str,
        top_k: int = 10,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search corpus with BM25 algorithm."""
        if not self.bm25 or not self.corpus_chunks:
            return []

        tokens = tokenize(query)
        if not tokens:
            return []

        scores = self.bm25.get_scores(tokens)
        
        # Max score normalization
        max_score = max(scores) if len(scores) > 0 and max(scores) > 0 else 1.0

        scored_candidates = []
        for idx, score in enumerate(scores):
            if score <= 0:
                continue
            chunk = self.corpus_chunks[idx]
            meta = chunk.get("metadata", {})

            # Isolation check
            chunk_user = meta.get("user_id")
            is_global = meta.get("is_global") in (True, "True", 1, "1")
            if user_id and chunk_user != user_id and not is_global:
                continue

            normalized_score = min(1.0, score / max_score)
            scored_candidates.append({
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "metadata": meta,
                "bm25_score": normalized_score,
                "raw_bm25": score
            })

        scored_candidates.sort(key=lambda x: x["bm25_score"], reverse=True)
        return scored_candidates[:top_k]

_bm25_instance: Optional[BM25SearchEngine] = None

def get_bm25_engine() -> BM25SearchEngine:
    global _bm25_instance
    if _bm25_instance is None:
        _bm25_instance = BM25SearchEngine()
    return _bm25_instance
