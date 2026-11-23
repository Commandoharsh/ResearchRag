import pytest

from backend.evaluation.hallucination import (
    hallucination_rate,
    sentence_support_scores,
)
from backend.evaluation.faithfulness import faithfulness_score
from backend.evaluation.answer_relevance import answer_relevance_score
from backend.evaluation.retrieval_metrics import (
    mean_reciprocal_rank,
    precision_at_k,
    ndcg_at_k,
    recall_at_k,
    reciprocal_rank,
)
from backend.evaluation.rag_evaluator import RAGEvaluator


def test_reciprocal_rank_is_inverse_of_first_relevant_rank():
    assert reciprocal_rank(
        ["irrelevant-a", "target", "irrelevant-b"],
        {"target"},
    ) == pytest.approx(0.5)


def test_reciprocal_rank_is_zero_when_no_relevant_result():
    assert reciprocal_rank(["a", "b"], {"target"}) == 0.0


def test_mean_reciprocal_rank_averages_queries():
    score = mean_reciprocal_rank(
        [["target", "x"], ["x", "target"], ["x"]],
        [{"target"}, {"target"}, {"target"}],
    )
    assert score == pytest.approx((1.0 + 0.5 + 0.0) / 3)


def test_mrr_rejects_mismatched_query_counts():
    with pytest.raises(ValueError):
        mean_reciprocal_rank([["a"]], [])


def test_precision_at_k_counts_relevant_results_in_returned_top_k():
    assert precision_at_k(
        ["target", "wrong", "target-2"],
        {"target", "target-2"},
        2,
    ) == pytest.approx(0.5)


def test_recall_at_k_uses_top_k_only():
    assert recall_at_k(
        ["wrong", "right", "also-right"],
        {"right", "also-right"},
        2,
    ) == pytest.approx(0.5)


def test_ndcg_rewards_relevant_results_earlier():
    best = ndcg_at_k(["a", "b", "x"], {"a", "b"}, 3)
    worse = ndcg_at_k(["x", "a", "b"], {"a", "b"}, 3)
    assert best == pytest.approx(1.0)
    assert 0.0 < worse < best


def test_ndcg_does_not_double_count_duplicate_chunks():
    score = ndcg_at_k(["relevant", "relevant"], {"relevant"}, 2)
    assert score == pytest.approx(1.0)


def test_faithfulness_baseline_is_one_for_context_tokens():
    assert faithfulness_score(
        "retrieval uses relevant documents",
        "retrieval uses relevant documents for generation",
    ) == pytest.approx(1.0)


def test_answer_relevance_baseline_detects_question_terms():
    assert answer_relevance_score(
        "How does retrieval work?",
        "Retrieval works by finding relevant documents.",
    ) > 0.0


def test_hallucination_rate_zero_when_all_sentences_supported():
    context = (
        "Retrieval finds relevant documents. "
        "Generation uses retrieved context."
    )
    answer = (
        "Retrieval finds relevant documents. "
        "Generation uses retrieved context."
    )
    assert hallucination_rate(answer, context) == pytest.approx(0.0)


def test_hallucination_rate_one_for_unsupported_sentence():
    context = "Retrieval finds relevant documents."
    answer = "Quantum satellites control ocean volcanoes."
    assert hallucination_rate(answer, context) == pytest.approx(1.0)


def test_hallucination_rate_is_fraction_of_unsupported_sentences():
    context = "Retrieval finds relevant documents."
    answer = (
        "Retrieval finds relevant documents. "
        "Quantum satellites control ocean volcanoes."
    )
    assert hallucination_rate(answer, context) == pytest.approx(0.5)


def test_sentence_support_scores_returns_one_score_per_sentence():
    scores = sentence_support_scores(
        "Retrieval finds relevant documents. Unsupported satellites orbit volcanoes.",
        "Retrieval finds relevant documents.",
    )
    assert len(scores) == 2
    assert scores[0] > scores[1]


def test_empty_answer_has_zero_hallucination_rate():
    assert hallucination_rate("", "some context") == 0.0


def test_rag_evaluator_exposes_quality_metrics():
    metrics = RAGEvaluator().evaluate(
        question="What does retrieval find?",
        answer="Retrieval finds relevant documents.",
        reference_answer="Retrieval finds relevant documents.",
        context="Retrieval finds relevant documents.",
    )
    assert {
        "answer_overlap",
        "faithfulness",
        "answer_relevance",
        "hallucination_rate_heuristic",
    }.issubset(metrics)
    assert metrics["hallucination_rate_heuristic"] == pytest.approx(0.0)
