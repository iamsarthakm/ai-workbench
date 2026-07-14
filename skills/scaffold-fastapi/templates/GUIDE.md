@AGENTS.md

This file provides guidance, when working with code in this repository.

## Project Overview

__PROJECT_NAME__ — __PROJECT_DESCRIPTION__

## Commands

```bash
# Install dependencies (uses uv, not pip)
uv sync --frozen --no-cache

# Run development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run database migrations
uv run alembic upgrade head

# Create a new migration after model changes
uv run alembic revision --autogenerate -m "description"

# Lint and format (Ruff)
uv run ruff check --fix app/
uv run ruff format app/

# Run tests
uv run pytest

# Run pre-commit hooks
uv tool run pre-commit run --files <changed-files>
```

## Architecture

Strict layered pattern: **Routes → Controllers → Services → Models**.

```
app/
├── routes/       # FastAPI routers — thin, only parse/validate requests
├── controllers/  # Business logic — orchestrate services, write to DB
├── services/     # External calls: third-party APIs, boto3/AWS SDK, other backends
├── models/       # SQLAlchemy ORM models
├── schemas/      # Pydantic request/response models
├── core/         # Config, JWT security, exception handling, small utilities
└── middleware/   # Request/response logging
```

Models are reachable from both controllers and services. Controllers are the
common path — fetch/write as part of handling a request. A service reaches into
models directly only when persisting something tied to its own external call
(e.g. logging that call's request/response for debugging) — otherwise services
should stay stateless and just return data to the controller that called them.


### Database

- PostgreSQL with async driver (`asyncpg`) via SQLAlchemy 2.0
- `app/database.py` exposes `Base`, `async_session_maker`, and the `get_db` FastAPI dependency
- Alembic migrations live in `alembic/` (async template); `alembic/env.py` reads the DB URL from `app.core.config.settings` and discovers models via `app/models/__init__.py`

### Authentication

`app/core/security.py` provides JWT bearer auth: `create_access_token` / `decode_access_token`, plus the `get_current_user` FastAPI dependency that resolves a Bearer token to a user id (see `app/routes/items.py` for a route that requires it). This scaffold does **not** include a login/registration flow — wire `create_access_token` into whichever auth mechanism this project needs (OTP, password, SSO, ...).

### Example resource

`app/routes/items.py`, `controllers/item.py`, `models/item.py`, `schemas/item.py` demonstrate the layered pattern end-to-end, including the authenticated write path. Replace or delete once real resources exist — see README.md's "Example resource" section for the exact commands (reset the migration too, not just the files).

## Environment Configuration

Settings in `app/core/config.py` (Pydantic, reads `.env`). Copy `.env.example` → `.env`.

**Deploy / local setup:** README.md


<!-- Renamed from claude.md to guide.md for making the skill tool agnostic -->