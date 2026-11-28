import pytest

from backend.cloud_config import (
    CloudConfigurationError,
    load_runtime_settings,
    validate_runtime_configuration,
)


def test_development_configuration_keeps_local_defaults(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    settings = validate_runtime_configuration()
    assert settings.environment == "development"
    assert settings.llm_provider == "ollama"


def test_production_requires_strong_jwt_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/researchrag")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("QDRANT_URL", "https://cluster.qdrant.io")
    monkeypatch.setenv("QDRANT_API_KEY", "qdrant-test-key")
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("JWT_SECRET_KEY", "short")
    monkeypatch.setenv("CORS_ORIGINS", "https://research.example.com")
    with pytest.raises(CloudConfigurationError, match="JWT_SECRET_KEY"):
        validate_runtime_configuration()


def test_production_rejects_non_https_cors(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/researchrag")
    monkeypatch.setenv("QDRANT_URL", "https://cluster.qdrant.io")
    monkeypatch.setenv("QDRANT_API_KEY", "qdrant-test-key")
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 48)
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:8080")
    with pytest.raises(CloudConfigurationError, match="HTTPS"):
        validate_runtime_configuration()


def test_production_requires_gemini_key(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/researchrag")
    monkeypatch.setenv("QDRANT_URL", "https://cluster.qdrant.io")
    monkeypatch.setenv("QDRANT_API_KEY", "qdrant-test-key")
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 48)
    monkeypatch.setenv("CORS_ORIGINS", "https://research.example.com")
    with pytest.raises(CloudConfigurationError, match="GEMINI_API_KEY"):
        validate_runtime_configuration()


def test_production_rejects_local_ollama_endpoint(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/researchrag")
    monkeypatch.setenv("QDRANT_URL", "https://cluster.qdrant.io")
    monkeypatch.setenv("QDRANT_API_KEY", "qdrant-test-key")
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 48)
    monkeypatch.setenv("CORS_ORIGINS", "https://research.example.com")
    with pytest.raises(CloudConfigurationError, match="localhost"):
        validate_runtime_configuration()


def test_production_accepts_valid_gemini_configuration(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("STORAGE_BACKEND", "r2")
    monkeypatch.setenv("R2_ENDPOINT_URL", "https://account.r2.cloudflarestorage.com")
    monkeypatch.setenv("R2_BUCKET_NAME", "researchrag")
    monkeypatch.setenv("R2_ACCESS_KEY_ID", "test-access-key")
    monkeypatch.setenv("R2_SECRET_ACCESS_KEY", "test-secret-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/researchrag")
    monkeypatch.setenv("QDRANT_URL", "https://cluster.qdrant.io")
    monkeypatch.setenv("QDRANT_API_KEY", "qdrant-test-key")
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("JWT_SECRET_KEY", "x" * 48)
    monkeypatch.setenv("CORS_ORIGINS", "https://research.example.com")
    settings = validate_runtime_configuration()
    assert settings.environment == "production"
    assert settings.cors_origins == ("https://research.example.com",)


def test_cors_origins_are_normalized(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("CORS_ORIGINS", " https://a.example.com/ , https://b.example.com ")
    settings = load_runtime_settings()
    assert settings.cors_origins == (
        "https://a.example.com",
        "https://b.example.com",
    )
