# ResearchRAG Observability

## HTTP diagnostics

- `GET /health/live`: process liveness; no network dependencies.
- `GET /health/ready`: readiness for the relational database, Qdrant, Redis, and Celery worker.
- `GET /health`: detailed dependency diagnostics, including embeddings and the configured LLM provider.
- `GET /metrics`: process-local HTTP request counts and latency aggregates.

Readiness returns HTTP 503 when a critical dependency is unavailable. Liveness remains HTTP 200 while the API process itself is running, allowing an orchestrator to distinguish a crashed process from a temporarily unavailable dependency.

## Structured logs

Set `LOG_LEVEL=INFO` (or DEBUG/WARNING/ERROR). API and worker processes emit one JSON object per line with UTC timestamp, severity, logger, message, and available request/task context. The API returns `X-Request-ID`; clients may supply a safe `X-Request-ID` value of up to 128 characters to correlate their own traces.

## Metrics limitations

The built-in metrics are process-local and reset when a process restarts. In a multi-worker or multi-replica deployment, each process reports only its own observations. They are intended for development and initial operational diagnosis, not durable SLO reporting. A later production phase should export OpenTelemetry metrics/traces to a shared collector.

## Container health check

The backend Docker health check should use `/health/live` so a temporary Redis/Qdrant outage does not cause Docker to restart a healthy API process. Use `/health/ready` as the deployment platform's readiness probe where supported.
