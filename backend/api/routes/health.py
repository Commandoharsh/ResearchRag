"""Liveness, readiness, and dependency health endpoints."""
import logging
import os
import time
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.rag.application import create_rag_application

logger = logging.getLogger("researchrag.health")
router = APIRouter(prefix="/health", tags=["Health"])


def _timed_check(check):
    started = time.perf_counter()
    try:
        details = check()
        return {
            "status": "healthy",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            **(details or {}),
        }
    except Exception as exc:
        logger.warning(
            "Dependency health check failed",
            extra={"dependency": getattr(check, "__name__", "unknown")},
            exc_info=True,
        )
        return {
            "status": "unhealthy",
            "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            "error": type(exc).__name__,
        }


def check_database() -> dict[str, Any]:
    application = create_rag_application()
    connection = application.database._connect()
    try:
        connection.execute("SELECT 1").fetchone()
    finally:
        connection.close()
    return {"engine": "postgresql" if application.database.is_postgres else "sqlite"}


def check_qdrant() -> dict[str, Any]:
    application = create_rag_application()
    vector_store = application.state.vector_store
    client = vector_store.client
    if client is None:
        raise RuntimeError("Qdrant client is not initialized")
    client.get_collections()
    return {"collection": vector_store.collection_name, "mode": "configured"}


def check_redis() -> dict[str, Any]:
    from redis import Redis

    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    client = Redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2)
    try:
        if not client.ping():
            raise RuntimeError("Redis did not respond to PING")
    finally:
        client.close()
    return {"broker": "reachable"}


def check_worker() -> dict[str, Any]:
    from backend.worker.celery_app import celery_app

    inspector = celery_app.control.inspect(timeout=1.5)
    workers = inspector.ping() or {}
    if not workers:
        raise RuntimeError("No Celery worker responded to ping")
    return {"workers": sorted(workers.keys())}


def check_llm() -> dict[str, Any]:
    import requests

    provider = settings.LLM_PROVIDER
    if provider == "gemini":
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        return {"provider": "gemini", "configuration": "present"}
    if provider == "ollama":
        base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        response = requests.get(f"{base_url}/api/tags", timeout=3)
        response.raise_for_status()
        models = [item.get("name") for item in response.json().get("models", [])]
        model_available = (
            settings.OLLAMA_MODEL in models
            or f"{settings.OLLAMA_MODEL}:latest" in models
        )
        if not model_available:
            raise RuntimeError(
                f"Configured Ollama model '{settings.OLLAMA_MODEL}' is not installed"
            )
        return {
            "provider": "ollama",
            "configured_model": settings.OLLAMA_MODEL,
            "model_available": True,
        }
    if provider == "mock":
        return {"provider": "mock", "configuration": "available"}
    raise RuntimeError(f"Unsupported LLM provider: {provider}")


def check_embeddings() -> dict[str, Any]:
    application = create_rag_application()
    model = application.state.embedding_model
    vector = model.encode(["ResearchRAG readiness probe"])
    if vector is None or len(vector) == 0:
        raise RuntimeError("Embedding model returned no vector")
    return {"dimension": len(vector[0])}


@router.get("/live")
def liveness():
    """Process liveness only; does not depend on external services."""
    return {"status": "alive", "service": "ResearchRAG"}


@router.get("/ready")
def readiness():
    """Readiness is successful only when critical dependencies respond."""
    checks = {
        "database": _timed_check(check_database),
        "qdrant": _timed_check(check_qdrant),
        "redis": _timed_check(check_redis),
        "worker": _timed_check(check_worker),
    }
    failed = [name for name, result in checks.items() if result["status"] != "healthy"]
    return JSONResponse(
        status_code=200 if not failed else 503,
        content={"status": "ready" if not failed else "not_ready", "checks": checks, "failed": failed},
    )


@router.get("")
def health_check():
    """Detailed dependency diagnostics, including embeddings and the LLM provider."""
    checks = {
        "database": _timed_check(check_database),
        "qdrant": _timed_check(check_qdrant),
        "redis": _timed_check(check_redis),
        "worker": _timed_check(check_worker),
        "embeddings": _timed_check(check_embeddings),
        "llm": _timed_check(check_llm),
    }
    failed = [name for name, result in checks.items() if result["status"] != "healthy"]
    return JSONResponse(
        status_code=200 if not failed else 503,
        content={
            "status": "healthy" if not failed else "degraded",
            "service": "ResearchRAG",
            "checks": checks,
            "unhealthy_services": failed,
        },
    )
