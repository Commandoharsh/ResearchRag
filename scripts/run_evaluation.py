"""
Run ResearchRAG retrieval and answer-quality evaluation.

Run from repository root:
    python -m scripts.run_evaluation

The built-in ground-truth chunk IDs are examples. For meaningful MRR/Recall/NDCG,
update backend/evaluation/dataset.py so relevant_chunks match IDs from your own
indexed documents.
"""
from datetime import datetime, timezone

from backend.evaluation.dataset import EVALUATION_DATASET
from backend.evaluation.rag_evaluator import RAGEvaluator
from backend.evaluation.retrieval_benchmark import RetrievalBenchmark
from backend.evaluation.report import EvaluationReport
from backend.rag.application import create_rag_application


def main():
    application = create_rag_application()

    try:
        print("Running retrieval benchmark...")
        retrieval = RetrievalBenchmark(application).run()

        print("Running answer-quality evaluation...")
        answer_quality = RAGEvaluator().evaluate(
            rag_service=application.rag_service,
            dataset=EVALUATION_DATASET,
        )

        report = {
            "project": "ResearchRAG",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "dataset_cases": len(EVALUATION_DATASET),
            "notes": [
                "Retrieval scores are only meaningful when relevant chunk IDs in "
                "backend/evaluation/dataset.py match the indexed corpus.",
                "hallucination_rate_heuristic is lexical overlap-based and is not "
                "a semantic factuality guarantee.",
                "LLM-as-a-judge evaluation is optional and is not run by this script.",
            ],
            "retrieval": retrieval,
            "answer_quality": answer_quality,
        }

        path = EvaluationReport().save(
            report,
            filename="researchrag_evaluation.json",
        )
        print(f"Evaluation report saved to: {path}")

        print("\nRetrieval summary:")
        for strategy, result in retrieval.items():
            print(f"  {strategy}: {result.get('metrics', {})}")

        print("\nAnswer quality summary:")
        print(answer_quality.get("metrics", {}))

    finally:
        application.close()


if __name__ == "__main__":
    main()
