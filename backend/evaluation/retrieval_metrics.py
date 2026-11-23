import math


def precision_at_k(retrieved_ids, relevant_ids, k=5):
    """Calculate Precision@K."""
    if k <= 0:
        raise ValueError("k must be greater than 0")

    relevant = set(relevant_ids)
    top_k = retrieved_ids[:k]

    if not top_k:
        return 0.0

    return sum(1 for item in top_k if item in relevant) / k


def recall_at_k(retrieved_ids, relevant_ids, k=5):
    """Calculate Recall@K."""
    if k <= 0:
        raise ValueError("k must be greater than 0")

    relevant = set(relevant_ids)

    if not relevant:
        return 0.0

    top_k = retrieved_ids[:k]
    retrieved_relevant = set(top_k) & relevant

    return len(retrieved_relevant) / len(relevant)


def reciprocal_rank(retrieved_ids, relevant_ids):
    """Calculate reciprocal rank of the first relevant result."""
    relevant = set(relevant_ids)

    for rank, item in enumerate(retrieved_ids, start=1):
        if item in relevant:
            return 1.0 / rank

    return 0.0


def mean_reciprocal_rank(all_retrieved, all_relevant):
    """Calculate Mean Reciprocal Rank across multiple queries."""
    if len(all_retrieved) != len(all_relevant):
        raise ValueError(
            "Retrieved query count must match relevant query count"
        )

    if not all_retrieved:
        return 0.0

    scores = [
        reciprocal_rank(retrieved, relevant)
        for retrieved, relevant in zip(all_retrieved, all_relevant)
    ]

    return sum(scores) / len(scores)


def ndcg_at_k(retrieved_ids, relevant_ids, k=5):
    """
    Calculate binary NDCG@K.

    Duplicate retrieved IDs are ignored after their first occurrence.
    """
    if k <= 0:
        raise ValueError("k must be greater than 0")

    relevant = set(relevant_ids)

    if not relevant:
        return 0.0

    # Remove duplicate chunks while preserving ranking order.
    unique_results = []
    seen = set()

    for item in retrieved_ids:
        if item not in seen:
            unique_results.append(item)
            seen.add(item)

    unique_results = unique_results[:k]

    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, item in enumerate(unique_results, start=1)
        if item in relevant
    )

    ideal_relevant_count = min(len(relevant), k)

    idcg = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(1, ideal_relevant_count + 1)
    )

    return dcg / idcg if idcg else 0.0