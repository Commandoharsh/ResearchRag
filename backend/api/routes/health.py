import sqlite3
import time
from pathlib import Path

import requests
from fastapi import APIRouter

from backend.config import settings
from backend.rag.application import create_rag_application


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


def check_sqlite():
    """Check SQLite database connectivity."""

    start = time.perf_counter()

    try:
        database_path = Path("data/researchrag.db")

        database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with sqlite3.connect(
            database_path,
            timeout=2,
        ) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        return {
            "status": "healthy",
            "latency_ms": round(latency_ms, 2),
            "database": str(database_path),
        }

    except Exception as exc:
        return {
            "status": "unhealthy",
            "error": str(exc),
        }


def check_qdrant():
    """
    Check the existing embedded Qdrant instance.

    IMPORTANT:
    Do not create another QdrantClient with the same
    local storage path. The application already owns it.
    """

    start = time.perf_counter()

    try:
        application = create_rag_application()

        vector_store = application.state.vector_store
        client = vector_store.client

        if client is None:
            raise RuntimeError(
                "Qdrant client is not initialized."
            )

        collections = client.get_collections()

        collection_names = [
            collection.name
            for collection in collections.collections
        ]

        expected_collection = vector_store.collection_name

        if expected_collection not in collection_names:
            raise RuntimeError(
                f"Collection '{expected_collection}' "
                "does not exist."
            )

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        return {
            "status": "healthy",
            "mode": "embedded",
            "collection": expected_collection,
            "latency_ms": round(latency_ms, 2),
        }

    except Exception as exc:
        return {
            "status": "unhealthy",
            "error": str(exc),
        }


def check_embeddings():
    """Check the initialized embedding model."""

    start = time.perf_counter()

    try:
        application = create_rag_application()

        embedding_model = application.state.embedding_model

        vector = embedding_model.encode(
            ["ResearchRAG health check"]
        )

        if vector is None or len(vector) == 0:
            raise RuntimeError(
                "Embedding model returned no vector."
            )

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        return {
            "status": "healthy",
            "model": "all-MiniLM-L6-v2",
            "dimension": len(vector[0]),
            "latency_ms": round(latency_ms, 2),
        }

    except Exception as exc:
        return {
            "status": "unhealthy",
            "error": str(exc),
        }


def check_ollama():
    """Check Ollama availability."""

    start = time.perf_counter()

    try:
        response = requests.get(
            f"{settings.OLLAMA_BASE_URL}/api/tags",
            timeout=3,
        )

        response.raise_for_status()

        data = response.json()

        models = [
            model.get("name")
            for model in data.get("models", [])
        ]

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        model_configured = (
            settings.OLLAMA_MODEL in models
            or f"{settings.OLLAMA_MODEL}:latest" in models
        )

        return {
            "status": "healthy",
            "base_url": settings.OLLAMA_BASE_URL,
            "configured_model": settings.OLLAMA_MODEL,
            "model_available": model_configured,
            "models": models,
            "latency_ms": round(latency_ms, 2),
        }

    except Exception as exc:
        return {
            "status": "unhealthy",
            "base_url": settings.OLLAMA_BASE_URL,
            "error": str(exc),
        }


@router.get("")
def health_check():
    """Detailed ResearchRAG health check."""

    services = {
        "sqlite": check_sqlite(),
        "qdrant": check_qdrant(),
        "embeddings": check_embeddings(),
        "ollama": check_ollama(),
    }

    unhealthy_services = [
        name
        for name, result in services.items()
        if result["status"] != "healthy"
    ]

    overall_status = (
        "healthy"
        if not unhealthy_services
        else "degraded"
    )

    return {
        "status": overall_status,
        "service": "ResearchRAG",
        "services": services,
        "unhealthy_services": unhealthy_services,
    }