"""Deterministic evaluation metrics for ResearchRAG.

These metrics assume binary relevance: a chunk ID is either relevant or not.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence


def _unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        value = str(item)
        if value not in seen:
            seen.add(value)
            output.append(value)
    return output


def precision_at_k(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be greater than zero")
    ranked = _unique(retrieved)[:k]
    return sum(item in relevant for item in ranked) / k


def recall_at_k_v2(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be greater than zero")
    if not relevant:
        raise ValueError("relevant must contain at least one chunk ID")
    ranked = _unique(retrieved)[:k]
    return sum(item in relevant for item in ranked) / len(relevant)


def reciprocal_rank_v2(retrieved: Sequence[str], relevant: set[str]) -> float:
    if not relevant:
        raise ValueError("relevant must contain at least one chunk ID")
    for rank, item in enumerate(_unique(retrieved), start=1):
        if item in relevant:
            return 1.0 / rank
    return 0.0


def ndcg_at_k_v2(retrieved: Sequence[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be greater than zero")
    if not relevant:
        raise ValueError("relevant must contain at least one chunk ID")
    ranked = _unique(retrieved)[:k]
    dcg = sum((1.0 / math.log2(rank + 1)) for rank, item in enumerate(ranked, 1) if item in relevant)
    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    return dcg / idcg if idcg else 0.0


def retrieval_metrics(retrieved: Sequence[str], relevant: set[str], k: int = 5) -> dict[str, float]:
    return {
        f"precision@{k}": precision_at_k(retrieved, relevant, k),
        f"recall@{k}": recall_at_k_v2(retrieved, relevant, k),
        "mrr": reciprocal_rank_v2(retrieved, relevant),
        f"ndcg@{k}": ndcg_at_k_v2(retrieved, relevant, k),
    }
