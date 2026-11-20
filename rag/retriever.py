"""
EduPath AI - Unified RAG Retriever Interface
Integrates hybrid search, reranking, thresholding, and citation preparation.
"""

from typing import List, Dict, Any, Optional
from backend.config import settings
from rag.hybrid_search import get_hybrid_engine
from rag.reranker import get_reranker
from rag.citations import build_citations
from security.prompt_injection import sanitize_retrieved_context

class EduPathRetriever:
    def __init__(self):
        self.hybrid_engine = get_hybrid_engine()
        self.reranker = get_reranker()

    def retrieve(
        self,
        query: str,
        user_id: Optional[str] = None,
        top_k: int = None,
        threshold: float = None,
        enable_rerank: bool = None
    ) -> Dict[str, Any]:
        """
        Unified retrieval method returning:
        {
            "chunks": List[Dict],
            "citations": List[Dict],
            "context_text": str,
            "has_context": bool
        }
        """
        limit = top_k or settings.RETRIEVAL_TOP_K
        min_thresh = threshold if threshold is not None else settings.RELEVANCE_THRESHOLD
        should_rerank = enable_rerank if enable_rerank is not None else settings.ENABLE_RERANKING

        # 1. Fetch candidates from Hybrid Search
        candidate_chunks = self.hybrid_engine.search(
            query=query,
            top_k=limit * 2,
            user_id=user_id
        )

        if not candidate_chunks:
            return {
                "chunks": [],
                "citations": [],
                "context_text": "",
                "has_context": False
            }

        # 2. Rerank candidates if enabled
        if should_rerank:
            final_chunks = self.reranker.rerank(
                query=query,
                candidates=candidate_chunks,
                top_k=limit,
                threshold=min_thresh
            )
        else:
            final_chunks = [c for c in candidate_chunks if c.get("hybrid_score", 0.0) >= min_thresh][:limit]

        if not final_chunks:
            return {
                "chunks": [],
                "citations": [],
                "context_text": "",
                "has_context": False
            }

        # 3. Generate verifiable citations
        citations = build_citations(final_chunks)

        # 4. Construct sanitized context string for LLM prompting
        context_parts = []
        for idx, c in enumerate(final_chunks, start=1):
            source = c.get("metadata", {}).get("source", "Knowledge Base")
            page = c.get("metadata", {}).get("page_number", 1)
            sanitized_body = sanitize_retrieved_context(c["text"])
            context_parts.append(f"[Source {idx}: {source}, Page {page}]\n{sanitized_body}")

        context_text = "\n\n".join(context_parts)

        return {
            "chunks": final_chunks,
            "citations": citations,
            "context_text": context_text,
            "has_context": True
        }

_retriever_instance: Optional[EduPathRetriever] = None

def get_retriever() -> EduPathRetriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = EduPathRetriever()
    return _retriever_instance
