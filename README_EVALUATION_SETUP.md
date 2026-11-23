# ResearchRAG – Complete Evaluation Test Pack

This pack adds tests for retrieval metrics, answer-quality heuristics, latency, citations, retrieval evaluator aggregation, and JSON report persistence. It does not overwrite existing project modules; it adds `metrics_v2.py`, new tests, and a dataset template.

## Important
- The answer relevance and faithfulness functions in the current project are lexical-overlap heuristics, not semantic verification.
- Citation tests validate citation-number parsing and mapping to retrieved results; they do not prove that a cited source truly supports a claim.
- Retrieval scores require a manually verified ground-truth dataset with actual chunk IDs from your indexed documents. The JSON template contains placeholders and must be edited before benchmarking.
- Do not open the embedded Qdrant storage from a second process while the Docker backend is running.

## Test command

```powershell
python -m pytest tests/test_retrieval_metrics_complete.py tests/test_answer_quality_metrics.py tests/test_latency_evaluation.py tests/test_citation_evaluation.py tests/test_evaluation_report.py tests/test_retrieval_evaluator.py -v
```

Or run the whole project test suite:

```powershell
python -m pytest -v
```

The first command is the evaluation-specific test suite. The second also runs your existing application tests and may reveal unrelated pre-existing failures.
