"""
EduPath AI - Dense + BM25 Hybrid Search
Combines dense semantic vector retrieval with BM25 keyword search using RRF and weighted fusion.
"""

from typing import List, Dict, Any, Optional
from backend.config import settings
from rag.vector_store import get_vector_store
from rag.bm25_search import get_bm25_engine

def reciprocal_rank_fusion(
    ranked_lists: List[List[Dict[str, Any]]],
    k: int = 60
) -> Dict[str, float]:
    """
    Standard Reciprocal Rank Fusion algorithm across multiple ranked retrieval lists.
    RRF(d) = sum(1 / (k + rank(d)))
    """
    rrf_scores: Dict[str, float] = {}
    for r_list in ranked_lists:
        for rank, item in enumerate(r_list, start=1):
            cid = item["chunk_id"]
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k + rank))
    return rrf_scores

class HybridSearchEngine:
    def __init__(self, alpha: float = None):
        # alpha is the weight for dense score; (1 - alpha) is for BM25
        self.alpha = alpha if alpha is not None else settings.HYBRID_ALPHA

    def search(
        self,
        query: str,
        top_k: int = 10,
        user_id: Optional[str] = None,
        alpha: Optional[float] = None,
        use_rrf: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute hybrid search: fetch candidates from both dense vector store and BM25 index,
        then combine their rankings.
        """
        weight_dense = alpha if alpha is not None else self.alpha
        weight_sparse = 1.0 - weight_dense

        vector_store = get_vector_store()
        bm25_engine = get_bm25_engine()

        # If BM25 has not been indexed, build from vector store
        if not bm25_engine.corpus_chunks and vector_store.count() > 0:
            bm25_engine.build_index(vector_store.get_all_chunks())

        # Retrieve top candidates from both channels
        dense_results = vector_store.search_dense(query=query, top_k=top_k * 2, user_id=user_id)
        sparse_results = bm25_engine.search(query=query, top_k=top_k * 2, user_id=user_id)

        # Merge candidate chunks
        candidates: Dict[str, Dict[str, Any]] = {}
        for item in dense_results:
            cid = item["chunk_id"]
            candidates[cid] = {
                "chunk_id": cid,
                "text": item["text"],
                "metadata": item["metadata"],
                "dense_score": item.get("dense_score", 0.0),
                "bm25_score": 0.0
            }

        for item in sparse_results:
            cid = item["chunk_id"]
            if cid in candidates:
                candidates[cid]["bm25_score"] = item.get("bm25_score", 0.0)
            else:
                candidates[cid] = {
                    "chunk_id": cid,
                    "text": item["text"],
                    "metadata": item["metadata"],
                    "dense_score": 0.0,
                    "bm25_score": item.get("bm25_score", 0.0)
                }

        merged_list = list(candidates.values())
        if not merged_list:
            return []

        if use_rrf:
            rrf_scores = reciprocal_rank_fusion([dense_results, sparse_results], k=60)
            for item in merged_list:
                item["hybrid_score"] = rrf_scores.get(item["chunk_id"], 0.0)
        else:
            # Linear combination
            for item in merged_list:
                d_score = item["dense_score"]
                s_score = item["bm25_score"]
                item["hybrid_score"] = (weight_dense * d_score) + (weight_sparse * s_score)

        merged_list.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return merged_list[:top_k]

_hybrid_instance: Optional[HybridSearchEngine] = None

def get_hybrid_engine() -> HybridSearchEngine:
    global _hybrid_instance
    if _hybrid_instance is None:
        _hybrid_instance = HybridSearchEngine()
    return _hybrid_instance
