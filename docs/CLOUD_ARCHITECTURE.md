# ResearchRAG Cloud Architecture

## Goal

Move ResearchRAG from a single-machine Docker Compose deployment to a cloud-ready, independently scalable application while preserving local Docker development.

This is a target architecture, not a claim that every integration is already implemented. Cloud deployment must wait until the persistence and configuration gates below are complete.

## Target topology

Browser
  -> Vercel (React + Vite frontend)
  -> HTTPS API requests and streaming
  -> Render or Railway (FastAPI API)
       -> Qdrant Cloud (vector retrieval)
       -> Neon / managed PostgreSQL (users, conversations, metadata, jobs)
       -> Cloudflare R2 / S3 (original documents and generated artifacts)
       -> Gemini API (hosted generation)

A separate background worker will process ingestion jobs and write results to PostgreSQL, object storage, and Qdrant.

## Proposed service choices

| Layer | Initial choice | Responsibility |
|---|---|---|
| Frontend | Vercel | React/Vite hosting, HTTPS, preview deployments |
| API | Render Docker web service | FastAPI, authentication, document/query endpoints |
| Vector database | Qdrant Cloud | Durable vector collections and filtered retrieval |
| Relational database | Neon PostgreSQL | Users, conversations, document metadata, job state |
| Object storage | Cloudflare R2 | Uploaded source files and generated artifacts |
| Hosted LLM | Gemini API | Production answer generation |
| Local model | Ollama | Local development only; not a cloud API dependency |
| Observability | Structured logs first; OpenTelemetry later | Request tracing, latency and failure diagnosis |

Provider choices can change without changing the logical architecture.

## Current repository constraints

The current Docker Compose setup starts the API, frontend, and Ollama. The API container mounts local /app/data and Hugging Face cache volumes, while Ollama stores models in a local Docker volume. Those volumes are useful for local development but are not a cloud persistence strategy.

The API Dockerfile intentionally runs one worker because the current embedded Qdrant/local filesystem setup uses a local lock. Do not increase API worker count or horizontally scale this deployment until vector storage is moved to a remote Qdrant service and all other process-local state is removed.

The current frontend build uses VITE_API_URL; this value is compiled into the frontend bundle and must be set to the public HTTPS API origin at build time. CORS must allow the exact deployed frontend origin.

## Migration principles

1. Keep local Docker Compose working during migration.
2. Put secrets in hosting-provider secret stores; never commit real values.
3. Replace local-only persistence before deploying multiple API instances.
4. Use remote Qdrant for vectors, PostgreSQL for transactional metadata, and object storage for source documents.
5. Make document ingestion idempotent and move long-running indexing to a background worker.
6. Keep hosted LLM credentials on the server; never expose them as Vite variables.
7. Add health/readiness checks and verify external dependencies before accepting traffic.
8. Run the evaluation suite against a fixed dataset before and after each retrieval change.

## Required environment configuration

The existing application already uses settings such as LLM_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL, JWT_SECRET_KEY, CORS_ORIGINS, and DATA_DIR.

The cloud migration will introduce settings for remote Qdrant, PostgreSQL, object storage, and worker execution only alongside code that consumes and validates them. Do not add unused environment variables and assume an integration is complete.

## Deployment gates

### Gate A — cloud-safe persistence
- [ ] Remote Qdrant client configured by environment.
- [ ] PostgreSQL migrations and connection lifecycle implemented.
- [ ] Uploaded files stored in R2/S3, not container filesystem.
- [ ] No essential state depends on a container-local volume.
- [ ] API startup fails clearly when required production configuration is missing.

### Gate B — production API
- [ ] Production CORS allowlist uses the deployed frontend origin.
- [ ] JWT secret is unique, strong, and stored as a platform secret.
- [ ] Authentication and authorization tests pass.
- [ ] Health and readiness endpoints distinguish process health from dependency readiness.
- [ ] Logs exclude credentials, tokens, and document contents.

### Gate C — production frontend
- [ ] Vercel project uses frontend as the root directory.
- [ ] Build command is npm run build.
- [ ] Output directory is dist.
- [ ] VITE_API_URL points to the public HTTPS API.
- [ ] Browser requests and streaming work against the deployed API.

### Gate D — reliability and evaluation
- [ ] Background indexing survives API restarts.
- [ ] Upload size/type validation is enforced server-side.
- [ ] Retrieval, citation, answer-quality, and latency benchmarks are recorded.
- [ ] Backups and retention policies are configured for databases and object storage.

## Cost-conscious first deployment

Start with the smallest suitable managed tiers and a hosted LLM API. Keep Ollama on the developer machine. Avoid a continuously running GPU instance until measured traffic and latency justify it. Free-tier availability, limits, and pricing can change; verify current provider terms before creating paid resources.

## Local development

Continue using the existing Compose workflow:

    docker compose up --build

The cloud migration should not remove or silently repurpose local development services.
