"""
EduPath AI - Retrieval Agent (Agent 2)
Dedicated to knowledge discovery, dense/sparse search execution, and citation grounding.
"""

from typing import Dict, Any, Optional
from rag.retriever import get_retriever
from rag.ingestion import ingest_document

class RetrievalAgent:
    def __init__(self):
        self.retriever = get_retriever()

    def search_knowledge_base(
        self,
        query: str,
        user_id: Optional[str] = None,
        top_k: int = 5,
        threshold: float = 0.25
    ) -> Dict[str, Any]:
        """
        Execute RAG retrieval pipeline and evaluate context quality.
        """
        result = self.retriever.retrieve(
            query=query,
            user_id=user_id,
            top_k=top_k,
            threshold=threshold,
            enable_rerank=True
        )

        has_sufficient_info = result["has_context"] and len(result["chunks"]) > 0

        return {
            "agent": "RetrievalAgent",
            "query": query,
            "has_context": has_sufficient_info,
            "chunks_count": len(result["chunks"]),
            "chunks": result["chunks"],
            "citations": result["citations"],
            "context_text": result["context_text"],
            "message": "Sufficient context found" if has_sufficient_info else "No relevant context found in knowledge base."
        }

    def ingest_new_document(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: Optional[str] = None,
        is_global: bool = False,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Delegate document ingestion."""
        return ingest_document(
            file_bytes=file_bytes,
            filename=filename,
            user_id=user_id,
            is_global=is_global,
            description=description
        )

_retrieval_agent_instance = None

def get_retrieval_agent() -> RetrievalAgent:
    global _retrieval_agent_instance
    if _retrieval_agent_instance is None:
        _retrieval_agent_instance = RetrievalAgent()
    return _retrieval_agent_instance
