from types import SimpleNamespace
from backend.evaluation.retrieval_evaluator import RetrievalEvaluator
from backend.evaluation.dataset import EvaluationCase


class FakeRetriever:
    def retrieve(self, query, top_k=5):
        assert query == "What is RAG?"
        assert top_k == 3
        return [SimpleNamespace(chunk_id=x) for x in ["x", "a", "b"]][:top_k]


def test_evaluate_case_returns_retrieval_metrics():
    evaluator = RetrievalEvaluator()
    results = [SimpleNamespace(chunk_id=x) for x in ["x", "a", "b"]]
    metrics = evaluator.evaluate_case(results, {"a", "b"})
    assert metrics["recall@1"] == 0.0
    assert metrics["recall@3"] == 1.0
    assert metrics["mrr"] == 0.5
    assert 0 <= metrics["ndcg@5"] <= 1


def test_evaluate_retriever_aggregates_cases():
    dataset = [EvaluationCase("case-1", "What is RAG?", {"a", "b"}, "Reference")]
    report = RetrievalEvaluator().evaluate(FakeRetriever(), dataset, top_k=3)
    assert len(report["cases"]) == 1
    assert report["cases"][0]["retrieved_chunks"] == ["x", "a", "b"]
    assert report["metrics"]["recall@3"] == 1.0


def test_aggregate_empty_cases_is_safe():
    report = RetrievalEvaluator()._aggregate([])
    assert report == {"cases": [], "metrics": {}}
