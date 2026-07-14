# __PROJECT_NAME__

__PROJECT_DESCRIPTION__

## Tech stack

| Layer | Stack |
|---|---|
| API | FastAPI, Python 3.12, uv |
| Data | PostgreSQL, SQLAlchemy, Alembic |
| Deploy | Docker Compose |
| Observability | Sentry |

API semver = `pyproject.toml` = OpenAPI `/docs`.

## Local setup

**Option A — direct (fastest inner loop).** Assumes Postgres is already running
locally (`localhost:5432` by default — adjust `DATABASE_URL` in `.env` if yours
is elsewhere or uses different credentials).

```bash
git clone <repo-url> && cd __PROJECT_SLUG__
uv sync --frozen --no-cache
cp .env.example .env   # fill in SECRET_KEY at minimum

createdb __DB_NAME__   # or: psql -h localhost -U postgres -c "CREATE DATABASE __DB_NAME__;"
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option B — fully containerized.** Bundles its own Postgres (host port `5433`,
so it doesn't clash with one you might already have on `5432`) and hot-reloads
the API on file changes — nothing to install locally except Docker.

```bash
cp .env.example .env   # fill in SECRET_KEY at minimum
docker compose -f docker-compose.dev.yml up --build
```

Generate migrations from the host either way (`uv sync` first if you're only
using Option B); against Option B's Postgres, point at its host port:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/__DB_NAME__ \
  uv run alembic revision --autogenerate -m "..."
```

## Deployment

```bash
cp .env.example .env   # fill in real values
docker compose up -d --build
curl -fsS http://localhost:8000/health/ready
```

**Env-only change (no code):** edit `.env`, then `docker compose up -d` (rebuild not required unless `Dockerfile`/`pyproject.toml` changed).

**Rollback:** if migrations shipped, `docker compose run --rm api uv run alembic downgrade <rev>` first, then redeploy the previous version.

## API documentation

- Local: http://localhost:8000/docs

## Example resource

`app/routes/items.py` → `controllers/item.py` → `models/item.py` →
`schemas/item.py` is a working example wired end-to-end (including the
authenticated write path) — kept only to prove the scaffold runs. Remove it
once you have real resources:

```bash
# Roll back and delete the example migration so alembic's history starts clean
uv run alembic downgrade base && rm -f alembic/versions/*.py

# Remove the example resource's files
rm -f app/models/item.py app/schemas/item.py app/controllers/item.py \
      app/routes/items.py tests/test_items.py
```

Then delete the `items_router` import and the
`app.include_router(items_router, ...)` line from `app/main.py`.

## For contributors

- Branch from `main`, open a PR
- Pre-commit/pre-push hooks: `uv tool run pre-commit install --hook-type pre-commit --hook-type pre-push`
  (runs ruff + gitleaks + mypy on every commit, the full test suite on push — there's no CI here, so these hooks are the enforcement)
- Lint: `uv run ruff check --fix app/` · `uv run ruff format app/`
- Types: `uv run mypy app`
- Tests: `uv run pytest`
- Migrations: `uv run alembic revision --autogenerate -m "..."` · `uv run alembic upgrade head`
