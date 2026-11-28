from unittest.mock import MagicMock

from backend.rag.retrieval.vector_store import create_qdrant_client


def test_create_qdrant_client_uses_local_path_by_default(monkeypatch, tmp_path):
    monkeypatch.delenv("QDRANT_URL", raising=False)
    monkeypatch.delenv("QDRANT_API_KEY", raising=False)

    client = MagicMock()
    constructor = MagicMock(return_value=client)

    import backend.rag.retrieval.vector_store as module
    monkeypatch.setattr(module, "QdrantClient", constructor)

    result = create_qdrant_client(str(tmp_path / "local-qdrant"))

    assert result is client
    constructor.assert_called_once_with(path=str(tmp_path / "local-qdrant"))


def test_create_qdrant_client_uses_remote_url_and_api_key(monkeypatch):
    client = MagicMock()
    constructor = MagicMock(return_value=client)

    import backend.rag.retrieval.vector_store as module
    monkeypatch.setattr(module, "QdrantClient", constructor)

    result = create_qdrant_client(
        url="https://example.qdrant.io:6333",
        api_key="test-only-key",
        timeout=12,
    )

    assert result is client
    constructor.assert_called_once_with(
        url="https://example.qdrant.io:6333",
        api_key="test-only-key",
        timeout=12,
    )


def test_create_qdrant_client_reads_environment(monkeypatch):
    client = MagicMock()
    constructor = MagicMock(return_value=client)

    import backend.rag.retrieval.vector_store as module
    monkeypatch.setattr(module, "QdrantClient", constructor)
    monkeypatch.setenv("QDRANT_URL", "https://cluster.qdrant.io")
    monkeypatch.setenv("QDRANT_API_KEY", "environment-test-key")

    create_qdrant_client()

    constructor.assert_called_once_with(
        url="https://cluster.qdrant.io",
        api_key="environment-test-key",
        timeout=30.0,
    )
