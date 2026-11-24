# ResearchRAG Cloud Migration Plan

This document tracks the implementation sequence for the cloud migration.

## Phase 1 — architecture and configuration baseline
- [x] Confirm repository and inspect existing Docker/API/frontend configuration.
- [x] Record target cloud architecture and migration gates.
- [x] Add production-only validation for JWT, HTTPS CORS, LLM credentials, and managed Qdrant.
- [ ] Keep local Compose defaults separate from production settings.

## Phase 2 — durable data services
- [x] Implement remote Qdrant client configuration while preserving local embedded mode.
- [ ] Implement managed PostgreSQL persistence and schema migrations.
- [ ] Move uploaded source documents to S3-compatible object storage.
- [ ] Add integration tests using service-level test configuration.
- [ ] Preserve a local development option.

## Phase 3 — ingestion reliability
- [ ] Add a durable indexing job model.
- [ ] Move long-running document extraction, embedding, and indexing to a worker.
- [ ] Add retries, idempotency, status reporting, and failure recovery.

## Phase 4 — retrieval quality
- [ ] Implement/verify hybrid dense + BM25 retrieval.
- [ ] Add fusion and configurable reranking.
- [ ] Add query decomposition for multi-part research questions.
- [ ] Add claim-level source verification.
- [ ] Compare changes using the existing evaluation and benchmark suite.

## Phase 5 — deployment and operations
- [ ] Deploy API only after Phases 2 and required parts of 3 are complete.
- [ ] Deploy frontend with the public API origin.
- [ ] Configure HTTPS, exact CORS origins, secrets, health checks, and logs.
- [ ] Run smoke tests for sign-in, upload, indexing, retrieval, citations, and streaming.
- [ ] Configure backups, limits, monitoring, and rollback.

## Security requirements
- Never commit .env, provider keys, JWT secrets, database URLs, or storage credentials.
- Rotate any credential that has appeared in terminal output, logs, screenshots, chat, or Git history.
- Keep all provider credentials server-side. Do not prefix secrets with VITE_.
- Use least-privilege service credentials and TLS for external services.
- Do not enable public document access unless explicitly required.
