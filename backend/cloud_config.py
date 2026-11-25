"""Production configuration validation for ResearchRAG.

This module validates security-critical production settings, including
PostgreSQL, Qdrant Cloud, and Cloudflare R2 configuration.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


class CloudConfigurationError(RuntimeError):
    """Raised when production environment configuration is unsafe or incomplete."""


@dataclass(frozen=True)
class RuntimeSettings:
    environment: str
    llm_provider: str
    cors_origins: tuple[str, ...]


def _value(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def load_runtime_settings() -> RuntimeSettings:
    """Read the small set of settings needed for safe application startup."""
    environment = _value("APP_ENV", "development").lower()
    provider = _value("LLM_PROVIDER", "ollama").lower()
    origins = tuple(
        origin.strip().rstrip("/")
        for origin in _value("CORS_ORIGINS").split(",")
        if origin.strip()
    )
    return RuntimeSettings(
        environment=environment,
        llm_provider=provider,
        cors_origins=origins,
    )


def validate_runtime_configuration() -> RuntimeSettings:
    """Validate production-only requirements; preserve local dev defaults."""
    settings = load_runtime_settings()

    if settings.environment not in {"production", "prod"}:
        return settings

    problems: list[str] = []

    jwt_secret = _value("JWT_SECRET_KEY")
    if len(jwt_secret) < 32 or jwt_secret.lower().startswith(
        ("replace-this", "change-me", "secret")
    ):
        problems.append("JWT_SECRET_KEY must be a unique secret of at least 32 characters")

    if not settings.cors_origins:
        problems.append("CORS_ORIGINS must contain the deployed frontend origin")
    elif any(not origin.startswith("https://") for origin in settings.cors_origins):
        problems.append("Every production CORS_ORIGINS entry must use HTTPS")

    if not _value("DATABASE_URL"):
        problems.append("DATABASE_URL is required for production relational persistence")
    if not _value("REDIS_URL"):
        problems.append("REDIS_URL is required for production background job processing")

    if not _value("QDRANT_URL"):
        problems.append("QDRANT_URL is required for production vector storage")
    if not _value("QDRANT_API_KEY"):
        problems.append("QDRANT_API_KEY is required for production vector storage")

    storage_backend = _value("STORAGE_BACKEND", "local").lower()
    if storage_backend != "r2":
        problems.append("STORAGE_BACKEND must be 'r2' in production")
    for variable in (
        "R2_ENDPOINT_URL",
        "R2_BUCKET_NAME",
        "R2_ACCESS_KEY_ID",
        "R2_SECRET_ACCESS_KEY",
    ):
        if not _value(variable):
            problems.append(f"{variable} is required when STORAGE_BACKEND=r2")

    if settings.llm_provider == "gemini" and not _value("GEMINI_API_KEY"):
        problems.append("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
    elif settings.llm_provider == "ollama":
        ollama_url = _value("OLLAMA_BASE_URL")
        if not ollama_url:
            problems.append("OLLAMA_BASE_URL is required when LLM_PROVIDER=ollama")
        elif "localhost" in ollama_url or "127.0.0.1" in ollama_url:
            problems.append("Cloud Ollama must use a reachable service URL, not localhost")
    elif settings.llm_provider not in {"gemini", "ollama"}:
        problems.append("LLM_PROVIDER must be either 'gemini' or 'ollama'")

    if problems:
        raise CloudConfigurationError(
            "Unsafe or incomplete production configuration: " + "; ".join(problems)
        )

    return settings
