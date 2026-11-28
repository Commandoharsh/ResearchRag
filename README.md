# ResearchRAG

An evaluation-focused Retrieval-Augmented Generation (RAG) system for
answering questions from a supplied document collection with retrieved
context and source citations.

ResearchRAG combines document ingestion, text chunking, embeddings,
vector retrieval, context construction, answer generation, and an
evaluation/benchmarking framework. Rather than relying on an LLM's
parametric knowledge alone, the pipeline retrieves relevant passages
from the indexed documents and uses those passages as grounding context
for generation.
    <img width="1273" height="758" alt="image" src="https://github.com/user-attachments/assets/f7416f5d-9c31-4cce-8db3-1918b4612bd9" />



> **Project status:** Active development. Configuration, supported
> providers, and deployment details may evolve. Check the source code
> and `.env.example` in this repository for the current
> implementation-specific settings.

## Key capabilities

### RAG pipeline

-   Document ingestion and text preparation.
-   Text chunking to create retrieval-sized passages.
-   Embedding generation and vector indexing.
-   Query preprocessing and query rewriting/multi-query support where
    configured.
-   Retrieval and context assembly.
-   LLM-based answer generation using retrieved context.
-   Citation extraction and citation-oriented response support.

### Evaluation and benchmarking

The evaluation package is designed to assess the pipeline beyond whether
it returns an answer. Current evaluation-related modules include:

-   `rag_evaluator.py` --- RAG evaluation orchestration.
-   `retrieval_metrics.py` --- retrieval metric calculations.
-   `metrics_v2.py` --- extended quality metrics.
-   `hallucination.py` --- hallucination-oriented evaluation.
-   `benchmark_runner.py` --- benchmark execution and result collection.

The repository also includes scripts and tests for answer quality,
retrieval quality, citations, latency, and benchmark reporting. Exact
metric definitions and required inputs are documented in the evaluation
setup and benchmark runner guides.

## Repository structure

``` text
ResearchRAG/
├── backend/
│   ├── evaluation/
│   │   ├── benchmark_runner.py
│   │   ├── hallucination.py
│   │   ├── metrics_v2.py
│   │   ├── rag_evaluator.py
│   │   └── retrieval_metrics.py
│   └── ...                 # API, RAG pipeline, database and supporting modules
├── data/
│   └── evaluation/
│       ├── chunk_inventory.csv
│       ├── evaluation_dataset.json
│       └── evaluation_dataset.template.json
├── frontend/               # Frontend application and Nginx configuration
├── scripts/
│   ├── run_benchmark.py
│   └── run_evaluation.py
├── tests/
│   ├── test_answer_quality_metrics.py
│   ├── test_benchmark_runner.py
│   ├── test_citation_evaluation.py
│   ├── test_evaluation_report.py
│   ├── test_latency_evaluation.py
│   ├── test_rag_quality_metrics.py
│   ├── test_retrieval_evaluator.py
│   └── test_retrieval_metrics_complete.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README_EVALUATION_SETUP.md
└── README_BENCHMARK_RUNNER.md
```

Other pipeline modules and supporting files are omitted from this
abbreviated tree.

## Requirements

-   Python version compatible with the dependencies pinned or specified
    in `requirements.txt`.
-   Git.
-   The configured vector database / storage backend required by your
    selected setup.
-   An LLM and embedding provider configured for your environment. Local
    Ollama integration may be used if supported by the current
    configuration.
-   Docker Desktop or Docker Engine if using the containerized
    deployment.

Check the project's configuration and `requirements.txt` before
installing or selecting provider versions.

## Installation

### 1. Clone the repository

``` bash
git clone https://github.com/Commandoharsh/ResearchRag.git
cd rag-pipeline
```

### 2. Create and activate a virtual environment

Windows PowerShell:

``` powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

``` bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using the example as a starting point. For local development, leave `QDRANT_URL` and `QDRANT_API_KEY` empty to use embedded Qdrant. For a managed Qdrant cluster, set both values; the vector-store client then uses the remote service:

``` powershell
Copy-Item .env.example .env
```

On macOS / Linux:

``` bash
cp .env.example .env
```

Set the values required by your selected model provider, embedding
provider, database/vector store, and application configuration. Do not
commit `.env` or put real credentials in `.env.example`.

## Running the application

The application entry points and required configuration can change as
the project develops. Inspect `backend/main.py`, the API route modules,
and `.env.example` for the current startup settings.

A common local development command, when the FastAPI application is
exposed as `app` from `backend.main`, is:

``` bash
uvicorn backend.main:app --reload
```

If the application object or import path differs in your checkout, use
the entry point defined in `backend/main.py`.

## Evaluation and benchmarks

ResearchRAG includes separate scripts for running evaluation and
benchmarks.

### Run evaluation

``` bash
python scripts/run_evaluation.py
```

### Run benchmarks

``` bash
python scripts/run_benchmark.py
```

Review the command-line options and configuration expected by each
script before execution. The evaluation data is located under
`data/evaluation/`. Use `evaluation_dataset.template.json` as a starting
point when preparing a custom dataset, and follow the schema expected by
the current evaluator.

Additional instructions: - [Evaluation
setup](README_EVALUATION_SETUP.md) - [Benchmark
runner](README_BENCHMARK_RUNNER.md)

### Evaluation considerations

-   Use a representative dataset of questions and expected
    evidence/answers.
-   Keep the evaluation dataset and configuration consistent when
    comparing runs.
-   Report retrieval quality separately from answer quality.
-   Inspect citation correctness and grounding; a fluent answer is not
    necessarily a supported answer.
-   Measure latency under comparable hardware, model, and concurrency
    conditions.
-   Treat automated hallucination and answer-quality scores as
    indicators for review, not proof that an answer is factually
    correct.
-   Record model/provider versions, embedding configuration, chunking
    settings, retrieval parameters, and dataset version alongside
    benchmark results.

## Running tests

Run the complete test suite from the repository root:

``` bash
python -m pytest tests/ -v
```

Run a specific evaluation test module:

``` bash
python -m pytest tests/test_benchmark_runner.py -v
```

For a concise test summary:

``` bash
python -m pytest tests/ -q
```

## Docker deployment

The repository includes `Dockerfile`, `docker-compose.yml`, and frontend
container configuration. Before starting the stack:

1.  Configure the required environment variables in `.env`.
2.  Review the services, ports, volumes, and health checks in
    `docker-compose.yml`.
3.  Confirm that required model and database services are available and
    correctly configured.

Start the configured services:

``` bash
docker compose up --build
```

Stop them:

``` bash
docker compose down
```

Do not assume that every external model or vector-store dependency is
automatically bundled in the containers; verify the compose
configuration for the services enabled in your checkout.

## Configuration and data

-   `.env.example` documents the environment-variable interface intended
    for local setup.
-   `data/evaluation/evaluation_dataset.json` contains the evaluation
    dataset currently tracked by the project.
-   `data/evaluation/evaluation_dataset.template.json` provides a
    template for preparing another dataset.
-   `data/evaluation/chunk_inventory.csv` contains chunk inventory data
    used by the evaluation workflow.

Do not add private documents, API keys, access tokens, personal
information, or other sensitive data to the public repository.

## Reproducibility

For meaningful comparisons between versions, record at least:

-   Dataset name and version.
-   Document collection and chunk inventory version.
-   Chunk size and overlap.
-   Embedding model and version.
-   Vector-store configuration.
-   Retrieval and reranking settings, if enabled.
-   Generation model and parameters.
-   Evaluation metric implementation/version.
-   Hardware, runtime environment, and concurrency settings.

A benchmark score is only comparable when the test data and relevant
configuration are held constant.

## Limitations

-   Generated answers depend on the quality, coverage, and freshness of
    the indexed documents.
-   Retrieval can miss relevant evidence or return irrelevant passages.
-   LLM output can contain unsupported statements even when context is
    supplied.
-   Citation extraction does not, by itself, guarantee that a citation
    supports the associated claim.
-   Evaluation results depend on dataset quality, metric design, and
    model/provider configuration.
-   Local model performance and latency depend on available hardware.

## Roadmap

Potential areas for continued development:

-   Expand benchmark datasets and regression testing.
-   Improve retrieval, reranking, and query transformation.
-   Strengthen claim-to-source citation verification.
-   Improve evaluation of groundedness and answer faithfulness.
-   Add repeatable experiment tracking and benchmark comparisons.
-   Improve deployment observability, error handling, and documentation.

## Contributing

1.  Create a feature branch.

2.  Make focused changes and add or update tests.

3.  Run the relevant tests, followed by the full test suite.

4.  Check formatting and whitespace:

    ``` bash
    git diff --check
    ```

5.  Submit a pull request describing the change and its test results.

## Author

**Harsh Rathore**\

## License

No license information is specified here. Unless a license file is added
to the repository, the project should not be assumed to grant permission
for reuse, modification, or redistribution.
