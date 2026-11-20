"""
EduPath AI - Reproducible RAG Evaluation Runner
Evaluates and benchmarks Dense vs. Hybrid vs. Hybrid+Reranker retrieval pipelines.
"""

import sys
from pathlib import Path

# Ensure root workspace is on python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from evaluation.benchmark_dataset import BENCHMARK_QUERIES
from evaluation.metrics import (
    calculate_recall_at_k, calculate_precision_at_k,
    calculate_reciprocal_rank, calculate_average_precision,
    calculate_citation_accuracy
)
from rag.vector_store import get_vector_store
from rag.bm25_search import get_bm25_engine
from rag.hybrid_search import get_hybrid_engine
from rag.reranker import get_reranker
from rag.citations import build_citations
from database.connection import init_db

def run_evaluation():
    init_db()
    vector_store = get_vector_store()
    bm25_engine = get_bm25_engine()
    hybrid_engine = get_hybrid_engine()
    reranker = get_reranker()

    # Synchronize BM25
    if not bm25_engine.corpus_chunks and vector_store.count() > 0:
        bm25_engine.build_index(vector_store.get_all_chunks())

    print("=" * 75)
    print("📊 EDUPATH AI - RAG PIPELINE BENCHMARK EVALUATION")
    print(f"Total Benchmark Queries: {len(BENCHMARK_QUERIES)}")
    print(f"Active Indexed Chunks:   {vector_store.count()}")
    print("=" * 75)

    pipelines = ["Dense Retrieval", "Hybrid (Dense+BM25)", "Hybrid + Reranking"]
    metrics_summary = {
        p: {"recall@5": [], "precision@5": [], "mrr": [], "map": [], "citation_acc": []}
        for p in pipelines
    }

    for item in BENCHMARK_QUERIES:
        query = item["query"]
        ground_truth = item["expected_sources"]

        # 1. Dense Retrieval
        dense_results = vector_store.search_dense(query=query, top_k=5)
        dense_sources = [c.get("metadata", {}).get("source", "") for c in dense_results]
        dense_citations = build_citations(dense_results)

        metrics_summary["Dense Retrieval"]["recall@5"].append(calculate_recall_at_k(dense_sources, ground_truth, k=5))
        metrics_summary["Dense Retrieval"]["precision@5"].append(calculate_precision_at_k(dense_sources, ground_truth, k=5))
        metrics_summary["Dense Retrieval"]["mrr"].append(calculate_reciprocal_rank(dense_sources, ground_truth))
        metrics_summary["Dense Retrieval"]["map"].append(calculate_average_precision(dense_sources, ground_truth))
        metrics_summary["Dense Retrieval"]["citation_acc"].append(calculate_citation_accuracy(dense_citations, ground_truth))

        # 2. Hybrid Retrieval
        hybrid_results = hybrid_engine.search(query=query, top_k=5)
        hybrid_sources = [c.get("metadata", {}).get("source", "") for c in hybrid_results]
        hybrid_citations = build_citations(hybrid_results)

        metrics_summary["Hybrid (Dense+BM25)"]["recall@5"].append(calculate_recall_at_k(hybrid_sources, ground_truth, k=5))
        metrics_summary["Hybrid (Dense+BM25)"]["precision@5"].append(calculate_precision_at_k(hybrid_sources, ground_truth, k=5))
        metrics_summary["Hybrid (Dense+BM25)"]["mrr"].append(calculate_reciprocal_rank(hybrid_sources, ground_truth))
        metrics_summary["Hybrid (Dense+BM25)"]["map"].append(calculate_average_precision(hybrid_sources, ground_truth))
        metrics_summary["Hybrid (Dense+BM25)"]["citation_acc"].append(calculate_citation_accuracy(hybrid_citations, ground_truth))

        # 3. Hybrid + Reranking
        candidates = hybrid_engine.search(query=query, top_k=10)
        reranked_results = reranker.rerank(query=query, candidates=candidates, top_k=5, threshold=0.1)
        reranked_sources = [c.get("metadata", {}).get("source", "") for c in reranked_results]
        reranked_citations = build_citations(reranked_results)

        metrics_summary["Hybrid + Reranking"]["recall@5"].append(calculate_recall_at_k(reranked_sources, ground_truth, k=5))
        metrics_summary["Hybrid + Reranking"]["precision@5"].append(calculate_precision_at_k(reranked_sources, ground_truth, k=5))
        metrics_summary["Hybrid + Reranking"]["mrr"].append(calculate_reciprocal_rank(reranked_sources, ground_truth))
        metrics_summary["Hybrid + Reranking"]["map"].append(calculate_average_precision(reranked_sources, ground_truth))
        metrics_summary["Hybrid + Reranking"]["citation_acc"].append(calculate_citation_accuracy(reranked_citations, ground_truth))

    # Print Report Table
    print(f"\n{'Pipeline Architecture':<25} | {'Recall@5':<10} | {'Prec@5':<10} | {'MRR':<10} | {'MAP':<10} | {'Citation Acc':<12}")
    print("-" * 88)

    results_table = {}
    for p in pipelines:
        avg_rec = sum(metrics_summary[p]["recall@5"]) / len(BENCHMARK_QUERIES)
        avg_prec = sum(metrics_summary[p]["precision@5"]) / len(BENCHMARK_QUERIES)
        avg_mrr = sum(metrics_summary[p]["mrr"]) / len(BENCHMARK_QUERIES)
        avg_map = sum(metrics_summary[p]["map"]) / len(BENCHMARK_QUERIES)
        avg_cit = sum(metrics_summary[p]["citation_acc"]) / len(BENCHMARK_QUERIES)

        results_table[p] = {
            "recall@5": avg_rec,
            "precision@5": avg_prec,
            "mrr": avg_mrr,
            "map": avg_map,
            "citation_acc": avg_cit
        }

        print(f"{p:<25} | {avg_rec:<10.4f} | {avg_prec:<10.4f} | {avg_mrr:<10.4f} | {avg_map:<10.4f} | {avg_cit:<12.4f}")

    print("-" * 88)
    print("\n✅ RAG Empirical Evaluation Completed Successfully.")
    return results_table

if __name__ == "__main__":
    run_evaluation()
