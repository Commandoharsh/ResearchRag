# ResearchRAG database migrations

ResearchRAG uses **Alembic** to version the PostgreSQL schema. Local SQLite
development keeps its existing automatic bootstrap so that tests and local
runs do not require a database server.

## Fresh PostgreSQL database

Set `DATABASE_URL` in the environment (use the provider's private connection
URL, never commit it), then run from the repository root:

```powershell
python -m pip install -r requirements.txt
alembic upgrade head
```

The initial revision creates `documents`, `users`, `conversations`, and
`messages`. The application does not create PostgreSQL tables at startup;
the deployment/release process must run migrations before starting the API.

## Existing PostgreSQL database created by the old application

Do **not** run `alembic upgrade head` against a database that already has
these tables but has no `alembic_version` table: the initial migration would
try to create them again.

First take a backup and verify that all four tables and their columns match
`backend/database/migrations/versions/0001_initial_schema.py`. Only after that
verification, baseline the existing schema:

```powershell
alembic stamp head
```

This records the current schema revision without executing DDL. If the schema
differs, create a corrective migration or reconcile it before stamping.

## Creating a future migration

After changing the schema, create a revision:

```powershell
alembic revision -m "describe the schema change"
```

Edit the generated `upgrade()` and `downgrade()` functions, review the SQL,
then apply it:

```powershell
alembic upgrade head
```

Inspect migration state:

```powershell
alembic current
alembic history
```

Always back up production data before applying migrations. Do not use
`alembic downgrade` in production without reviewing the downgrade operations
and confirming that they cannot destroy required data.
