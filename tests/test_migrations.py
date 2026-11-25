from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


ROOT = Path(__file__).resolve().parents[1]


def test_alembic_configuration_points_to_migrations():
    config = Config(str(ROOT / "alembic.ini"))
    assert config.get_main_option("script_location") == "backend/database/migrations"


def test_initial_schema_is_the_single_head_revision():
    config = Config(str(ROOT / "alembic.ini"))
    scripts = ScriptDirectory.from_config(config)

    assert scripts.get_current_head() == "0001_initial_schema"

    revision = scripts.get_revision("0001_initial_schema")
    assert revision is not None
    assert revision.down_revision is None


def test_postgres_schema_is_not_created_by_runtime_bootstrap():
    source = (ROOT / "backend" / "database" / "database.py").read_text(
        encoding="utf-8"
    )
    assert "if self.is_postgres:" in source
    assert "PostgreSQL schema lifecycle is owned by Alembic migrations." in source
