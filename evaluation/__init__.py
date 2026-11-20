"""
EduPath AI - Evaluation Package
"""

from evaluation.benchmark_dataset import BENCHMARK_QUERIES
from evaluation.metrics import (
    calculate_recall_at_k, calculate_precision_at_k,
    calculate_reciprocal_rank, calculate_average_precision,
    calculate_citation_accuracy
)
from evaluation.evaluate_rag import run_evaluation

__all__ = [
    "BENCHMARK_QUERIES",
    "calculate_recall_at_k",
    "calculate_precision_at_k",
    "calculate_reciprocal_rank",
    "calculate_average_precision",
    "calculate_citation_accuracy",
    "run_evaluation",
]
