"""
EduPath AI - Reranking Engine
Re-scores candidate chunks using query term proximity, semantic coverage, and exact matches.
"""

from typing import List, Dict, Any
import re
from backend.config import settings

class CandidateReranker:
    def __init__(self, proximity_weight: float = 0.3, coverage_weight: float = 0.4, base_weight: float = 0.3):
        self.proximity_weight = proximity_weight
        self.coverage_weight = coverage_weight
        self.base_weight = base_weight

    def _calculate_query_coverage(self, query_terms: List[str], text_lower: str) -> float:
        if not query_terms:
            return 0.0
        matched = sum(1 for term in query_terms if term in text_lower)
        return matched / len(query_terms)

    def _calculate_term_proximity(self, query_terms: List[str], text_lower: str) -> float:
        if len(query_terms) < 2:
            return 1.0 if (query_terms and query_terms[0] in text_lower) else 0.0

        positions = []
        for term in query_terms:
            match = re.search(r"\b" + re.escape(term) + r"\b", text_lower)
            if match:
                positions.append(match.start())

        if len(positions) < 2:
            return 0.2 if len(positions) == 1 else 0.0

        positions.sort()
        span = positions[-1] - positions[0]
        # Shorter span means higher term density and relevance
        proximity_score = max(0.0, 1.0 - (span / max(len(text_lower), 500)))
        return proximity_score

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank a list of candidate chunks.
        Computes an adjusted rerank score for each candidate and returns the top_k.
        """
        if not candidates:
            return []

        min_threshold = threshold if threshold is not None else settings.RELEVANCE_THRESHOLD
        query_terms = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 2]

        reranked = []
        for item in candidates:
            text_lower = item["text"].lower()
            base_score = item.get("hybrid_score", item.get("dense_score", 0.5))

            coverage = self._calculate_query_coverage(query_terms, text_lower)
            proximity = self._calculate_term_proximity(query_terms, text_lower)

            rerank_score = (
                (self.base_weight * base_score) +
                (self.coverage_weight * coverage) +
                (self.proximity_weight * proximity)
            )

            # Cap between 0 and 1
            final_score = min(1.0, max(0.0, rerank_score))

            if final_score >= min_threshold:
                new_item = dict(item)
                new_item["rerank_score"] = final_score
                reranked.append(new_item)

        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]

_reranker_instance: CandidateReranker = None

def get_reranker() -> CandidateReranker:
    global _reranker_instance
    if _reranker_instance is None:
        _reranker_instance = CandidateReranker()
    return _reranker_instance
