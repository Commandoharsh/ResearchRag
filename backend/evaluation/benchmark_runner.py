"""Reproducible retrieval and optional end-to-end benchmark for ResearchRAG.

Ground truth is supplied by the user in JSON. This module never invents labels.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from backend.evaluation.metrics_v2 import (
    precision_at_k, recall_at_k_v2, reciprocal_rank_v2, ndcg_at_k_v2,
)


@dataclass
class BenchmarkCase:
    id: str
    question: str
    relevant_chunks: set[str]
    reference_answer: str = ""
    expected_sources: set[str] | None = None
    answerable: bool = True


def load_dataset(path: str | Path) -> list[BenchmarkCase]:
    """Load explicitly labelled cases from a JSON array or {"cases": [...]} ."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Evaluation dataset not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    rows = raw.get("cases") if isinstance(raw, dict) else raw
    if not isinstance(rows, list) or not rows:
        raise ValueError("Dataset must contain a non-empty JSON array or a 'cases' array.")
    cases: list[BenchmarkCase] = []
    seen: set[str] = set()
    for i, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f"Dataset item {i} must be an object.")
        case_id = str(row.get("id", "")).strip()
        question = str(row.get("question", "")).strip()
        relevant = row.get("relevant_chunks", [])
        if not case_id or not question:
            raise ValueError(f"Dataset item {i} requires non-empty 'id' and 'question'.")
        if case_id in seen:
            raise ValueError(f"Duplicate evaluation case id: {case_id}")
        seen.add(case_id)
        if not isinstance(relevant, list) or not all(isinstance(x, str) and x.strip() for x in relevant):
            raise ValueError(f"Case {case_id}: relevant_chunks must be a list of chunk ID strings.")
        if row.get("answerable", True) and not relevant:
            raise ValueError(f"Case {case_id}: answerable cases require at least one relevant_chunks ID.")
        expected_sources = row.get("expected_sources") or []
        cases.append(BenchmarkCase(
            id=case_id,
            question=question,
            relevant_chunks=set(relevant),
            reference_answer=str(row.get("reference_answer", "")),
            expected_sources=set(str(x) for x in expected_sources),
            answerable=bool(row.get("answerable", True)),
        ))
    return cases


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def _mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def _chunk_id(result: Any) -> str:
    value = getattr(result, "chunk_id", None)
    if value is None and isinstance(result, dict):
        value = result.get("chunk_id")
    if value is None:
        raise ValueError(f"Retriever result has no chunk_id: {type(result).__name__}")
    return str(value)


def _metadata(result: Any) -> dict:
    value = getattr(result, "metadata", None)
    if value is None and isinstance(result, dict):
        value = result.get("metadata", {})
    return value if isinstance(value, dict) else {}


class RetrievalBenchmarkRunner:
    """Runs the four retrieval strategies against the same labelled questions."""

    def __init__(self, application: Any, top_k: int = 5):
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        self.application = application
        self.top_k = top_k
        state = getattr(application, "state", None)
        self.strategies = {
            "semantic": application.semantic_retriever,
            "bm25": getattr(state, "bm25_retriever", None),
            "hybrid": application.hybrid_retriever,
            "hybrid_reranker": application.reranking_pipeline,
        }
        self.strategies = {name: obj for name, obj in self.strategies.items() if obj is not None}

    def run(self, cases: list[BenchmarkCase], include_generation: bool = False) -> dict:
        if not cases:
            raise ValueError("At least one labelled evaluation case is required.")
        all_ids = {chunk.chunk_id for chunk in self.application.state.vector_store.get_all_chunks()}
        missing = sorted({cid for case in cases for cid in case.relevant_chunks if cid not in all_ids})
        if missing:
            raise ValueError(
                "Ground-truth chunk IDs are not present in the current Qdrant collection: "
                + ", ".join(missing[:20])
                + (f" ... ({len(missing)} total)" if len(missing) > 20 else "")
                + ". Export the chunk inventory and correct your labelled dataset."
            )

        per_strategy: dict[str, list[dict]] = {}
        for name, retriever in self.strategies.items():
            rows = []
            for case in cases:
                started = time.perf_counter()
                results = retriever.retrieve(case.question, top_k=self.top_k)
                elapsed_ms = (time.perf_counter() - started) * 1000
                ids = [_chunk_id(result) for result in results]
                if case.answerable:
                    metrics = {
                        f"precision@{self.top_k}": precision_at_k(ids, case.relevant_chunks, self.top_k),
                        f"recall@{self.top_k}": recall_at_k_v2(ids, case.relevant_chunks, self.top_k),
                        "mrr": reciprocal_rank_v2(ids, case.relevant_chunks),
                        f"ndcg@{self.top_k}": ndcg_at_k_v2(ids, case.relevant_chunks, self.top_k),
                    }
                else:
                    metrics = {f"precision@{self.top_k}": None, f"recall@{self.top_k}": None,
                               "mrr": None, f"ndcg@{self.top_k}": None}
                returned_sources = sorted({str(_metadata(r).get("source", "")) for r in results if _metadata(r).get("source")})
                expected = case.expected_sources or set()
                source_recall = (len(expected.intersection(returned_sources)) / len(expected)) if expected else None
                rows.append({
                    "case_id": case.id, "question": case.question,
                    "retrieved_chunk_ids": ids, "retrieved_sources": returned_sources,
                    "latency_ms": elapsed_ms, "metrics": metrics,
                    "expected_source_recall": source_recall,
                })
            per_strategy[name] = rows

        metric_names = [f"precision@{self.top_k}", f"recall@{self.top_k}", "mrr", f"ndcg@{self.top_k}"]
        summary = {}
        for name, rows in per_strategy.items():
            summary[name] = {
                "evaluated_cases": len(rows),
                "answerable_cases": sum(c.answerable for c in cases),
                "metrics": {metric: _mean([r["metrics"][metric] for r in rows if r["metrics"][metric] is not None])
                            for metric in metric_names},
                "latency_ms": {
                    "mean": _mean([r["latency_ms"] for r in rows]),
                    "p50": _percentile([r["latency_ms"] for r in rows], .50),
                    "p95": _percentile([r["latency_ms"] for r in rows], .95),
                    "min": min((r["latency_ms"] for r in rows), default=0.0),
                    "max": max((r["latency_ms"] for r in rows), default=0.0),
                },
                "mean_expected_source_recall": _mean([r["expected_source_recall"] for r in rows if r["expected_source_recall"] is not None])
                    if any(r["expected_source_recall"] is not None for r in rows) else None,
            }

        report = {
            "schema_version": "1.0",
            "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "top_k": self.top_k,
            "dataset_cases": len(cases),
            "ground_truth": "user_labelled_chunk_ids",
            "strategies": summary,
            "case_results": per_strategy,
            "generation_evaluation": None,
            "notes": [
                "Only user-labelled relevant chunk IDs are scored.",
                "Latency is measured in-process and is affected by machine load and model warm-up.",
                "Unanswerable cases are excluded from retrieval relevance averages; abstention/generation evaluation is not scored here.",
                "Expected source recall is computed only when expected_sources are supplied.",
            ],
        }
        if include_generation:
            report["generation_evaluation"] = self._run_generation(cases)
        return report

    def _run_generation(self, cases: list[BenchmarkCase]) -> list[dict]:
        """Optional end-to-end RAG timing and transparent lexical proxy metrics."""
        from backend.evaluation.answer_metrics import answer_keyword_overlap
        from backend.evaluation.answer_relevance import answer_relevance_score
        from backend.evaluation.faithfulness import faithfulness_score
        output = []
        for case in cases:
            started = time.perf_counter()
            response = self.application.query(case.question)
            total_ms = (time.perf_counter() - started) * 1000
            answer = str(response.get("answer", ""))
            context = str(response.get("context", ""))
            metrics_obj = response.get("metrics")
            metrics = metrics_obj.__dict__ if hasattr(metrics_obj, "__dict__") else (metrics_obj or {})
            citations = response.get("citations", [])
            cited_ids = [getattr(c, "chunk_id", None) or (c.get("chunk_id") if isinstance(c, dict) else None) for c in citations]
            valid_ids = {getattr(r, "chunk_id", None) or (r.get("chunk_id") if isinstance(r, dict) else None)
                         for r in response.get("results", [])}
            cited_ids = [str(x) for x in cited_ids if x]
            citation_validity = (sum(cid in valid_ids for cid in cited_ids) / len(cited_ids)) if cited_ids else 0.0
            output.append({
                "case_id": case.id, "answer": answer, "total_latency_ms": total_ms,
                "stage_metrics": metrics,
                "reference_answer_overlap_heuristic": answer_keyword_overlap(case.reference_answer, answer) if case.reference_answer else None,
                "answer_relevance_heuristic": answer_relevance_score(case.question, answer),
                "faithfulness_lexical_heuristic": faithfulness_score(answer, context),
                "citation_validity": citation_validity,
                "citation_count": len(cited_ids),
                "answerable": case.answerable,
            })
        return output


def export_chunk_inventory(application: Any, output_path: str | Path) -> Path:
    """Export current indexed chunk IDs and metadata for manual ground-truth labelling."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chunks = application.state.vector_store.get_all_chunks()
    rows = [{"chunk_id": c.chunk_id, "source": c.metadata.get("source", ""),
             "page": c.metadata.get("page", ""), "chunk_index": c.metadata.get("chunk_index", ""),
             "content": c.content} for c in chunks]
    if output_path.suffix.lower() == ".csv":
        with output_path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["chunk_id", "source", "page", "chunk_index", "content"])
            writer.writeheader(); writer.writerows(rows)
    else:
        output_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def write_reports(report: dict, output_dir: str | Path) -> dict[str, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "benchmark_report.json"
    csv_path = output_dir / "benchmark_case_results.csv"
    md_path = output_dir / "benchmark_report.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    flat = []
    for strategy, rows in report["case_results"].items():
        for row in rows:
            flat.append({"strategy": strategy, "case_id": row["case_id"], "question": row["question"],
                         "retrieved_chunk_ids": " | ".join(row["retrieved_chunk_ids"]),
                         "retrieved_sources": " | ".join(row["retrieved_sources"]),
                         "latency_ms": row["latency_ms"], **row["metrics"]})
    fields = list(dict.fromkeys(k for row in flat for k in row))
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        if fields:
            writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(flat)
    lines = ["# ResearchRAG Benchmark Report", "", f"- Run ID: `{report['run_id']}`",
             f"- Cases: {report['dataset_cases']}", f"- K: {report['top_k']}", "",
             "## Retrieval strategy comparison", "",
             "| Strategy | Precision | Recall | MRR | nDCG | Mean ms | P95 ms |", "|---|---:|---:|---:|---:|---:|---:|"]
    for name, item in report["strategies"].items():
        m, t = item["metrics"], item["latency_ms"]
        precision = m.get(f"precision@{report['top_k']}", 0) or 0.0
        recall = m.get(f"recall@{report['top_k']}", 0) or 0.0
        ndcg = m.get(f"ndcg@{report['top_k']}", 0) or 0.0
        lines.append(f"| {name} | {precision:.4f} | {recall:.4f} | {m.get('mrr', 0) or 0.0:.4f} | {ndcg:.4f} | {t['mean']:.2f} | {t['p95']:.2f} |")
    lines += ["", "## Interpretation notes", ""] + [f"- {x}" for x in report.get("notes", [])]
    if report.get("generation_evaluation"):
        lines += ["", "## End-to-end generation checks", "",
                  "Generation quality values below are lexical heuristics, not semantic truth verification.", ""]
        for row in report["generation_evaluation"]:
            lines.append(f"- {row['case_id']}: end-to-end {row['total_latency_ms']:.2f} ms; "
                         f"reference overlap={row['reference_answer_overlap_heuristic']}; "
                         f"answer relevance={row['answer_relevance_heuristic']:.4f}; "
                         f"faithfulness lexical heuristic={row['faithfulness_lexical_heuristic']:.4f}; "
                         f"citation validity={row['citation_validity']:.4f}")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": json_path, "csv": csv_path, "markdown": md_path}
