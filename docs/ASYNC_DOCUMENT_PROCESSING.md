# Asynchronous document processing

ResearchRAG uses Celery workers and Redis so PDF ingestion no longer runs
inside the upload request.

## Local Docker architecture

- FastAPI receives and validates the PDF (25 MB limit).
- The file is persisted through the configured local/R2 storage adapter.
- A document row is created with status `uploaded`.
- A Celery task is queued in Redis; the API responds with HTTP 202.
- The worker downloads the object, indexes it, and updates the row to
  `indexing`, `indexed`, or `failed`.
- The frontend can poll `GET /documents/{document_id}` for status.

Docker Compose uses a Qdrant server container by default. This is intentional:
the API and worker are separate processes and must not both open Qdrant's
embedded local filesystem database. Set `QDRANT_URL` and optionally
`QDRANT_API_KEY` to use Qdrant Cloud instead.

## Start services

From the repository root:

```powershell
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs -f backend worker redis qdrant
```

The first build can take time because the API and worker share the ML dependencies.

## Upload and monitor

Use the frontend upload flow or POST a multipart PDF to `/index/pdf`.
A successful queue response looks like:

```json
{
  "status": "queued",
  "document_id": "<document-uuid>",
  "task_id": "<celery-task-id>",
  "filename": "paper.pdf"
}
```

Then poll:

```http
GET /documents/<document-uuid>
```

The document status changes as the worker processes it.

## Retry and delivery behavior

Tasks are acknowledged after execution, use a worker prefetch of one, and
retry up to three times with a 15-second delay. Failed tasks update the
document record to `failed` with an error message.

The task is designed to be retryable. Qdrant upserts use deterministic chunk
point identifiers, so retrying an indexing operation does not create duplicate
vector points.

## Production deployment

Provision managed Redis (or another supported Redis service), PostgreSQL,
Qdrant Cloud, and Cloudflare R2. Set `REDIS_URL` to the managed Redis URL in
both the API and worker environments. Deploy the same backend image twice:
once with the API command and once with the Celery worker command:

```bash
celery -A backend.worker.celery_app:celery_app worker --loglevel=INFO --concurrency=1
```

Keep API and worker environment variables consistent, especially database,
Qdrant, Redis, storage, and model settings. Do not run the worker against
embedded local Qdrant storage.
