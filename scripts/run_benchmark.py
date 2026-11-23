from __future__ import annotations
import argparse
import sys
from pathlib import Path

# Ensure repository root is importable when executed as a script.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.evaluation.benchmark_runner import (
    RetrievalBenchmarkRunner, export_chunk_inventory, load_dataset, write_reports,
)
from backend.rag.application import create_rag_application


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ResearchRAG retrieval benchmark.")
    parser.add_argument("--dataset", default="data/evaluation/evaluation_dataset.json")
    parser.add_argument("--output-dir", default="data/evaluation")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--export-inventory", action="store_true", help="Export Qdrant chunk IDs to CSV/JSON, then exit.")
    parser.add_argument("--inventory-format", choices=["csv", "json"], default="csv")
    parser.add_argument("--include-generation", action="store_true", help="Also run full RAG answers; invokes configured LLM.")
    args = parser.parse_args()
    app = None
    try:
        app = create_rag_application()
        if args.export_inventory:
            path = Path(args.output_dir) / f"chunk_inventory.{args.inventory_format}"
            export_chunk_inventory(app, path)
            print(f"Exported indexed chunk inventory: {path}")
            return 0
        cases = load_dataset(args.dataset)
        print(f"Loaded {len(cases)} labelled evaluation cases.")
        runner = RetrievalBenchmarkRunner(app, top_k=args.top_k)
        report = runner.run(cases, include_generation=args.include_generation)
        paths = write_reports(report, args.output_dir)
        print("\nBenchmark complete. Strategy summary:")
        for name, result in report["strategies"].items():
            metrics = result["metrics"]
            print(f"{name:18} P@{args.top_k}={metrics[f'precision@{args.top_k}']:.4f} "
                  f"R@{args.top_k}={metrics[f'recall@{args.top_k}']:.4f} "
                  f"MRR={metrics['mrr']:.4f} nDCG@{args.top_k}={metrics[f'ndcg@{args.top_k}']:.4f} "
                  f"mean={result['latency_ms']['mean']:.2f}ms P95={result['latency_ms']['p95']:.2f}ms")
        print("\nReports:")
        for kind, path in paths.items():
            print(f"{kind}: {path}")
        return 0
    except Exception as exc:
        print(f"BENCHMARK FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    finally:
        if app is not None:
            app.close()


if __name__ == "__main__":
    raise SystemExit(main())
