from unittest.mock import MagicMock

from backend.database.database import Database, _PostgresConnection


def test_database_defaults_to_sqlite(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    database = Database(database_path=str(tmp_path / "researchrag.db"))
    assert database.is_postgres is False
    assert database.database_path.exists()


def test_postgres_adapter_translates_qmark_placeholders():
    raw = MagicMock()
    wrapped = _PostgresConnection(raw)

    wrapped.execute(
        "SELECT * FROM users WHERE email = ? AND is_active = ?",
        ("user@example.com", 1),
    )

    raw.execute.assert_called_once_with(
        "SELECT * FROM users WHERE email = %s AND is_active = %s",
        ("user@example.com", 1),
    )


def test_database_selects_postgres_from_environment(monkeypatch):
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://user:pass@db.example.com:5432/researchrag",
    )
    database = Database.__new__(Database)
    database.database_url = (
        "postgresql://user:pass@db.example.com:5432/researchrag"
    )
    database.is_postgres = bool(database.database_url)
    assert database.is_postgres is True
