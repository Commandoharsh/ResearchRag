"""Database connection adapter for local SQLite and managed PostgreSQL.

Existing repositories use SQLite-style qmark placeholders. The small
PostgreSQL adapter below translates those placeholders and returns mapping
rows, allowing the repositories to keep their current interface while the
application migrates to a managed PostgreSQL service.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any


class _PostgresConnection:
    def __init__(self, connection: Any):
        self._connection = connection

    def execute(self, query: str, parameters=()):
        # All current repository queries use positional qmark placeholders.
        return self._connection.execute(query.replace("?", "%s"), parameters)

    def commit(self):
        self._connection.commit()

    def close(self):
        self._connection.close()

    def __enter__(self):
        self._connection.__enter__()
        return self

    def __exit__(self, exc_type, exc, traceback):
        try:
            return self._connection.__exit__(exc_type, exc, traceback)
        finally:
            self._connection.close()


class Database:
    def __init__(
        self,
        database_path: str = "data/researchrag.db",
        database_url: str | None = None,
    ):
        self.database_url = (
            database_url or os.getenv("DATABASE_URL", "")
        ).strip()
        self.is_postgres = bool(self.database_url)

        if self.is_postgres:
            self.database_path = None
        else:
            self.database_path = Path(database_path)
            self.database_path.parent.mkdir(parents=True, exist_ok=True)

        self._initialize()

    def _connect(self):
        if self.is_postgres:
            try:
                import psycopg
                from psycopg.rows import dict_row
            except ImportError as exc:
                raise RuntimeError(
                    "PostgreSQL support requires psycopg[binary]. "
                    "Install project requirements before setting DATABASE_URL."
                ) from exc

            url = self.database_url
            if url.startswith("postgres://"):
                url = "postgresql://" + url[len("postgres://"):]

            connection = psycopg.connect(
                url,
                row_factory=dict_row,
                connect_timeout=10,
            )
            return _PostgresConnection(connection)

        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        # SQLite does not enforce foreign keys unless enabled per connection.
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    error_message TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(conversation_id) REFERENCES conversations(id)
                )
                """
            )
            connection.commit()
