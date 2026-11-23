import math
import pytest

from backend.evaluation.metrics_v2 import (
    precision_at_k, recall_at_k_v2, reciprocal_rank_v2,
    ndcg_at_k_v2, retrieval_metrics,
)


def test_precision_at_k_counts_relevant_results_only():
    assert precision_at_k(["a", "x", "b"], {"a", "b"}, 3) == pytest.approx(2 / 3)


def test_precision_at_k_uses_k_as_denominator_when_fewer_results():
    assert precision_at_k(["a"], {"a"}, 5) == pytest.approx(0.2)


def test_precision_at_k_removes_duplicate_ids():
    assert precision_at_k(["a", "a", "x"], {"a"}, 3) == pytest.approx(1 / 3)


def test_recall_at_k():
    assert recall_at_k_v2(["x", "a", "b"], {"a", "b", "c"}, 3) == pytest.approx(2 / 3)


def test_recall_at_k_zero_when_no_relevant_retrieved():
    assert recall_at_k_v2(["x", "y"], {"a"}, 2) == 0.0


def test_reciprocal_rank_uses_first_relevant_rank():
    assert reciprocal_rank_v2(["x", "y", "b", "a"], {"a", "b"}) == pytest.approx(1 / 3)


def test_reciprocal_rank_zero_when_no_hit():
    assert reciprocal_rank_v2(["x", "y"], {"a"}) == 0.0


def test_ndcg_perfect_ranking_is_one():
    assert ndcg_at_k_v2(["a", "b", "x"], {"a", "b"}, 3) == pytest.approx(1.0)


def test_ndcg_penalizes_relevant_chunk_at_lower_rank():
    assert ndcg_at_k_v2(["x", "a", "b"], {"a", "b"}, 3) < 1.0


def test_ndcg_duplicate_ids_do_not_inflate_score():
    score = ndcg_at_k_v2(["a", "a", "x"], {"a"}, 3)
    assert score == pytest.approx(1.0)


@pytest.mark.parametrize("metric", [precision_at_k, ndcg_at_k_v2])
def test_k_must_be_positive_for_k_metrics(metric):
    with pytest.raises(ValueError):
        metric(["a"], {"a"}, 0)


def test_recall_requires_nonempty_ground_truth():
    with pytest.raises(ValueError):
        recall_at_k_v2(["a"], set(), 2)


def test_mrr_requires_nonempty_ground_truth():
    with pytest.raises(ValueError):
        reciprocal_rank_v2(["a"], set())


def test_ndcg_requires_nonempty_ground_truth():
    with pytest.raises(ValueError):
        ndcg_at_k_v2(["a"], set(), 2)


def test_retrieval_metrics_returns_expected_keys_and_values():
    result = retrieval_metrics(["a", "x", "b"], {"a", "b"}, 3)
    assert set(result) == {"precision@3", "recall@3", "mrr", "ndcg@3"}
    assert result["precision@3"] == pytest.approx(2 / 3)
    assert result["recall@3"] == 1.0
    assert result["mrr"] == 1.0
    assert 0 <= result["ndcg@3"] <= 1
