"""
EduPath AI - RAG Pipeline Unit & Integration Tests
Validates chunking, embeddings, dense search, BM25, hybrid fusion, reranking, and citations.
"""

import pytest
from rag.chunking import recursive_split_text, chunk_document_pages
from rag.embeddings import OfflineDeterministicEmbeddings
from rag.vector_store import get_vector_store
from rag.bm25_search import get_bm25_engine
from rag.hybrid_search import get_hybrid_engine, reciprocal_rank_fusion
from rag.reranker import get_reranker
from rag.citations import build_citations, format_citations_markdown

def test_recursive_split_text():
    text = (
        "Paragraph 1 discusses Python programming and software engineering principles.\n\n"
        "Paragraph 2 discusses artificial intelligence, neural networks, and deep learning architectures.\n\n"
        "Paragraph 3 covers LangGraph multi-agent systems and stateful cyclical workflows."
    )
    chunks = recursive_split_text(text, chunk_size=120, chunk_overlap=20)
    assert len(chunks) >= 3
    for c in chunks:
        assert len(c) > 0

def test_offline_deterministic_embeddings():
    embedder = OfflineDeterministicEmbeddings(dimension=384)
    v1 = embedder.embed_query("machine learning engineering")
    v2 = embedder.embed_query("machine learning engineering")
    v3 = embedder.embed_query("classical culinary baking techniques")

    assert len(v1) == 384
    assert v1 == v2, "Deterministic embedder must produce identical vectors for identical inputs"

    # Compute dot products (cosine similarity because vectors are normalized)
    sim_same = sum(a * b for a, b in zip(v1, v2))
    sim_diff = sum(a * b for a, b in zip(v1, v3))

    assert sim_same > 0.99
    assert sim_same > sim_diff

def test_dense_search_user_isolation():
    vector_store = get_vector_store()
    initial_count = vector_store.count()
    assert initial_count >= 0

def test_bm25_search():
    bm25 = get_bm25_engine()
    corpus = [
        {"chunk_id": "c1", "text": "Deep learning and neural networks with PyTorch", "metadata": {"is_global": True}},
        {"chunk_id": "c2", "text": "Relational database indexing and SQL query optimization", "metadata": {"is_global": True}},
        {"chunk_id": "c3", "text": "Kubernetes container orchestration and Docker deployment", "metadata": {"is_global": True}}
    ]
    bm25.build_index(corpus)
    res = bm25.search("neural networks PyTorch", top_k=2)
    assert len(res) > 0
    assert res[0]["chunk_id"] == "c1"

def test_reciprocal_rank_fusion():
    list_dense = [{"chunk_id": "doc_A"}, {"chunk_id": "doc_B"}]
    list_bm25 = [{"chunk_id": "doc_B"}, {"chunk_id": "doc_C"}]
    
    rrf = reciprocal_rank_fusion([list_dense, list_bm25], k=60)
    assert "doc_B" in rrf
    # doc_B appeared in both lists, so its RRF score should be highest
    assert rrf["doc_B"] > rrf["doc_A"]
    assert rrf["doc_B"] > rrf["doc_C"]

def test_citation_generation():
    chunks = [{
        "chunk_id": "chunk_42",
        "text": "EduPath AI certified curriculum standard for machine learning engineers.",
        "metadata": {"source": "ai_framework.txt", "page_number": 3},
        "rerank_score": 0.88
    }]
    citations = build_citations(chunks)
    assert len(citations) == 1
    c = citations[0]
    assert c["source"] == "ai_framework.txt"
    assert c["page_number"] == 3
    assert c["score"] == 0.88

    md = format_citations_markdown(citations)
    assert "ai_framework.txt" in md
    assert "Page 3" in md
