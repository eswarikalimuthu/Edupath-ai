"""
EduPath AI - RAG Package
"""

from rag.extraction import extract_document
from rag.cleaning import clean_text
from rag.chunking import chunk_document_pages, recursive_split_text, DocumentChunk
from rag.embeddings import get_embedding_model, BaseEmbeddings, OfflineDeterministicEmbeddings
from rag.vector_store import get_vector_store, ChromaVectorStore
from rag.bm25_search import get_bm25_engine, BM25SearchEngine
from rag.hybrid_search import get_hybrid_engine, HybridSearchEngine
from rag.reranker import get_reranker, CandidateReranker
from rag.citations import build_citations, format_citations_markdown, Citation
from rag.retriever import get_retriever, EduPathRetriever
from rag.ingestion import ingest_document, IngestionError

__all__ = [
    "extract_document",
    "clean_text",
    "chunk_document_pages",
    "recursive_split_text",
    "DocumentChunk",
    "get_embedding_model",
    "BaseEmbeddings",
    "OfflineDeterministicEmbeddings",
    "get_vector_store",
    "ChromaVectorStore",
    "get_bm25_engine",
    "BM25SearchEngine",
    "get_hybrid_engine",
    "HybridSearchEngine",
    "get_reranker",
    "CandidateReranker",
    "build_citations",
    "format_citations_markdown",
    "Citation",
    "get_retriever",
    "EduPathRetriever",
    "ingest_document",
    "IngestionError",
]
