# ResearchRAG benchmark runner

This add-on compares the live application's four retrieval paths: semantic, BM25, hybrid, and hybrid + reranker. It reads the existing embedded Qdrant collection through the application's single `RAGApplication` instance. It does not create a second Qdrant client.

## Important: Docker named-volume and embedded Qdrant lock

Your Compose configuration stores `/app/data` in the named Docker volume `researchrag_data`. A local Windows Python process will not automatically see that same data. Therefore run the benchmark in a one-off backend container, using the same named volume, while the normal backend container is stopped. Do not start a second Qdrant client while the normal backend is running. Never run `docker compose down -v` or delete the `researchrag_data` volume.

## Merge from PowerShell

Assuming the ZIP is in Downloads and your repo is `C:\Users\harsh\ResearchRAG`:

```powershell
cd C:\Users\harsh\ResearchRAG
$zip = "$env:USERPROFILE\Downloads\researchrag-benchmark-runner.zip"
$tmp = "$env:TEMP\researchrag-benchmark-runner"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
Expand-Archive -Path $zip -DestinationPath $tmp -Force
$src = Join-Path $tmp "researchrag-benchmark-runner"
Copy-Item "$src\backend\evaluation\benchmark_runner.py" ".\backend\evaluation\benchmark_runner.py" -Force
Copy-Item "$src\scripts\run_benchmark.py" ".\scripts\run_benchmark.py" -Force
New-Item -ItemType Directory -Force ".\data\evaluation" | Out-Null
Copy-Item "$src\data\evaluation\evaluation_dataset.template.json" ".\data\evaluation\evaluation_dataset.template.json" -Force
Copy-Item "$src\tests\test_benchmark_runner.py" ".\tests\test_benchmark_runner.py" -Force
Copy-Item "$src\README_BENCHMARK_RUNNER.md" ".\README_BENCHMARK_RUNNER.md" -Force
```

These are new files. Existing evaluation modules and tests are not replaced.

## 1. Rebuild the backend image after merging

```powershell
docker compose build backend
```

## 2. Stop only the normal backend service

```powershell
docker compose stop backend
```

Leave Ollama and the frontend alone. This releases the embedded Qdrant lock. Your named volume and indexed data remain intact.

## 3. Export the actual indexed chunk inventory from the same Docker volume

First create the host-side evaluation folder:

```powershell
New-Item -ItemType Directory -Force .\data\evaluation | Out-Null
docker compose run --rm --no-deps -v "${PWD}/data/evaluation:/app/data/evaluation" backend python scripts/run_benchmark.py --export-inventory --inventory-format csv
```

The one-off container reads the real Qdrant collection from the `researchrag_data` named volume, while the extra bind mount makes the exported CSV visible at `data/evaluation/chunk_inventory.csv` on Windows. Do not run the local Windows Python command for this Docker deployment: it would likely inspect a different, empty Qdrant directory.

Open `chunk_inventory.csv`, find the chunks that genuinely support each question, and copy their exact `chunk_id` values into the labelled dataset. `expected_sources` should contain the exact source filenames. Do not label relevance based only on similar wording; inspect the chunk content.

## 3. Create your labelled dataset

Copy the template:

```powershell
Copy-Item data/evaluation/evaluation_dataset.template.json data/evaluation/evaluation_dataset.json
notepad data/evaluation/evaluation_dataset.json
```

Replace all example text and IDs. Include multiple relevant chunk IDs where appropriate. Every answerable case must have at least one relevant chunk. For a genuinely unanswerable question, set `answerable` to `false` and `relevant_chunks` to `[]`; retrieval ranking metrics are omitted for that case.

## 4. Run the retrieval benchmark

```powershell
python scripts/run_benchmark.py --dataset data/evaluation/evaluation_dataset.json --top-k 5
```

To also run full answer generation through the configured LLM (slower and may incur API/local compute cost):

```powershell
python scripts/run_benchmark.py --dataset data/evaluation/evaluation_dataset.json --top-k 5 --include-generation
```

The optional generation section includes end-to-end time, stage timings, reference-answer lexical overlap, question-answer lexical relevance, lexical answer-context overlap, and citation mapping validity. These lexical measures are heuristics, not proof of semantic correctness or hallucination-free answers. Citation validity checks that returned citation chunk IDs are present among the retrieved chunks; it does not establish that a source substantively supports a claim.

## 5. Restart backend

```powershell
docker compose start backend
```

## Outputs

- `data/evaluation/benchmark_report.json`
- `data/evaluation/benchmark_case_results.csv`
- `data/evaluation/benchmark_report.md`
- `data/evaluation/chunk_inventory.csv` (after export)

## Tests

```powershell
python -m pytest tests/test_benchmark_runner.py -v
```

The benchmark does not claim accuracy until you create and review a representative ground-truth dataset. Compare strategies on the same cases and report the number of labelled questions alongside all scores.
