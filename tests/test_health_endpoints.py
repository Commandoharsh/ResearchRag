from backend.api.routes import health


def test_liveness_does_not_depend_on_external_services():
    assert health.liveness() == {
        "status": "alive",
        "service": "ResearchRAG",
    }


def test_readiness_returns_503_when_critical_dependency_fails(monkeypatch):
    monkeypatch.setattr(health, "check_database", lambda: {})
    monkeypatch.setattr(
        health,
        "check_qdrant",
        lambda: (_ for _ in ()).throw(RuntimeError("qdrant offline")),
    )
    monkeypatch.setattr(health, "check_redis", lambda: {})
    monkeypatch.setattr(health, "check_worker", lambda: {"workers": ["worker@local"]})

    response = health.readiness()

    assert response.status_code == 503
    assert b'"status":"not_ready"' in response.body
    assert b'"qdrant"' in response.body


def test_readiness_returns_200_when_critical_dependencies_are_healthy(monkeypatch):
    monkeypatch.setattr(health, "check_database", lambda: {"engine": "sqlite"})
    monkeypatch.setattr(health, "check_qdrant", lambda: {"collection": "research"})
    monkeypatch.setattr(health, "check_redis", lambda: {"broker": "reachable"})
    monkeypatch.setattr(health, "check_worker", lambda: {"workers": ["worker@local"]})

    response = health.readiness()

    assert response.status_code == 200
    assert b'"status":"ready"' in response.body
