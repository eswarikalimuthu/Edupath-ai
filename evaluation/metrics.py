"""
EduPath AI - RAG Evaluation Metrics Suite
Implements Precision@K, Recall@K, Mean Reciprocal Rank (MRR), and MAP.
"""

from typing import List, Set, Dict, Any

def calculate_recall_at_k(retrieved_sources: List[str], ground_truth_sources: List[str], k: int = 5) -> float:
    """Recall@K = (relevant items retrieved in top K) / (total relevant items)"""
    if not ground_truth_sources:
        return 1.0
    top_k = retrieved_sources[:k]
    matched = sum(1 for src in ground_truth_sources if any(src.lower() in t.lower() for t in top_k))
    return matched / len(ground_truth_sources)

def calculate_precision_at_k(retrieved_sources: List[str], ground_truth_sources: List[str], k: int = 5) -> float:
    """Precision@K = (relevant items retrieved in top K) / K"""
    if k <= 0:
        return 0.0
    top_k = retrieved_sources[:k]
    matched = sum(1 for t in top_k if any(src.lower() in t.lower() for src in ground_truth_sources))
    return matched / len(top_k) if top_k else 0.0

def calculate_reciprocal_rank(retrieved_sources: List[str], ground_truth_sources: List[str]) -> float:
    """Reciprocal Rank = 1 / rank of first relevant item"""
    for rank, item in enumerate(retrieved_sources, start=1):
        if any(src.lower() in item.lower() for src in ground_truth_sources):
            return 1.0 / rank
    return 0.0

def calculate_average_precision(retrieved_sources: List[str], ground_truth_sources: List[str]) -> float:
    """Average Precision (AP) across all recall levels."""
    if not ground_truth_sources:
        return 1.0
    hits = 0
    sum_precisions = 0.0
    for rank, item in enumerate(retrieved_sources, start=1):
        if any(src.lower() in item.lower() for src in ground_truth_sources):
            hits += 1
            sum_precisions += hits / rank
    return sum_precisions / len(ground_truth_sources) if hits > 0 else 0.0

def calculate_citation_accuracy(citations: List[Dict[str, Any]], ground_truth_sources: List[str]) -> float:
    """Percentage of citations that point to verified relevant ground-truth documents."""
    if not citations:
        return 0.0
    valid_citations = 0
    for cit in citations:
        src = cit.get("source", "").lower()
        if any(gt.lower() in src for gt in ground_truth_sources):
            valid_citations += 1
    return valid_citations / len(citations)
