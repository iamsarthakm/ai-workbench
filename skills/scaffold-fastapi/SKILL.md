---
name: scaffold-fastapi
description: Scaffold a new production-ready FastAPI service — layered architecture (routes/controllers/services/models), async Postgres via SQLAlchemy 2.0 + Alembic, JWT auth, structured JSON logging, Sentry, Docker + Docker Compose (dev and prod), tests, and repo hygiene files. Use real tooling (uv, alembic) for anything the tooling can produce; copy curated content from this skill's templates/ for everything else.
---

# Scaffold a new FastAPI service

This skill builds a new FastAPI backend from scratch, reproducing a pattern already
proven in production (Routes → Controllers → Services → Models, async SQLAlchemy,
JWT bearer auth, structured logging, Sentry, Alembic). It is meant to be read by a
human directly, or executed step by step by Claude — every step below is either a
real shell command or a `cp` of a file from `templates/` (relative to this SKILL.md).

**Guardrails — read before running anything:**
- Do not scaffold into a non-empty directory without confirming with the user first.
- Do not `git commit` automatically. Leave the working tree staged/unstaged for the
  user to review. Only commit if they explicitly ask as part of invoking this skill.
- Do not push to any remote, ever, as part of this skill.
- Step 11 brings up `docker-compose.dev.yml`'s own Postgres + API containers to
  verify the scaffold end-to-end — tear them down (`docker compose ... down`,
  already the last line of that step) rather than leaving them running.

Let `$SKILL_DIR` be the absolute path of the directory containing this SKILL.md
(all `cp`/`cp -R` commands below are written relative to `$SKILL_DIR/templates/`).

Steps 0–11 share shell variables (`PROJECT_NAME`, `PROJECT_SLUG`,
`PROJECT_DESCRIPTION`, `DB_NAME`, `TARGET_DIR`, `SKILL_DIR`). Run them in one
continuous shell session, or re-export the values at the top of each new one —
a fresh shell (including a new tool call in a non-interactive harness) does not
remember variables from a previous one.

## Step 0 — Collect inputs

Ask the user for these in a plain text message (not a multiple-choice tool) —
they're open-ended free-text answers, not a small set of discrete options, so a
choice-based question tool will reject the call:

1. **Project name** — human-readable, e.g. "Payments Service" → `PROJECT_NAME`
2. **One-line description** → `PROJECT_DESCRIPTION`
3. **Target directory** — a new folder to create, or "here" if already in an empty dir
4. Confirm the derived slug/DB name below rather than silently assuming them.

Derive defaults, then confirm with the user before proceeding:

```bash
PROJECT_NAME="Payments Service"
PROJECT_DESCRIPTION="Backend API for processing merchant payouts."

# kebab-case slug, e.g. "payments-service"
PROJECT_SLUG=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr -s ' _' '-' | tr -cd 'a-z0-9-')

# snake_case DB name (Postgres identifiers don't like hyphens), e.g. "payments_service"
DB_NAME=$(echo "$PROJECT_SLUG" | tr '-' '_')
```

## Step 1 — Create and enter the target directory

```bash
mkdir -p "$TARGET_DIR" && cd "$TARGET_DIR"
```

If scaffolding in the current directory instead, confirm it's empty first
(`ls -la`) — don't overwrite existing work.

## Step 2 — Bootstrap with uv (the real tool, not hand-rolled)

```bash
uv init --name "$PROJECT_SLUG" --python 3.12
ls -la   # see what uv generated
rm -f main.py hello.py   # remove uv's placeholder entrypoint script (name varies by uv version); harmless if absent
```

`uv init` also runs `git init` and writes `.python-version` — leave both.

## Step 3 — Overwrite the placeholder pyproject.toml / README with curated versions

```bash
cp "$SKILL_DIR/templates/pyproject.toml" pyproject.toml
cp "$SKILL_DIR/templates/README.md" README.md
```

## Step 4 — Application package

```bash
mkdir -p app
cp -R "$SKILL_DIR/templates/app/." app/
```

This brings in `main.py`, `database.py`, and the `core/`, `middleware/`,
`models/`, `routes/`, `schemas/`, `controllers/`, `services/` packages — including a small working example resource (`item`) wired end-to-end
(route → controller → model → DB, with one authenticated endpoint) so the scaffold
is provably correct rather than an empty shell. Replace or delete the `item`
example once real resources exist — Step 12 has ready-made commands for this.

## Step 5 — Tests

```bash
mkdir -p tests
cp -R "$SKILL_DIR/templates/tests/." tests/
```

## Step 6 — Dotfiles, editor config, PR template, Docker

```bash
cp "$SKILL_DIR/templates/dotfiles/env.example" .env.example
cp "$SKILL_DIR/templates/dotfiles/gitignore" .gitignore
cp "$SKILL_DIR/templates/dotfiles/dockerignore" .dockerignore
cp "$SKILL_DIR/templates/dotfiles/cursorignore" .cursorignore
cp "$SKILL_DIR/templates/dotfiles/pre-commit-config.yaml" .pre-commit-config.yaml

mkdir -p .vscode
cp "$SKILL_DIR/templates/vscode/settings.json" .vscode/settings.json
cp "$SKILL_DIR/templates/vscode/extensions.json" .vscode/extensions.json

mkdir -p .github
cp "$SKILL_DIR/templates/github/pull_request_template.md" .github/PULL_REQUEST_TEMPLATE.md

cp "$SKILL_DIR/templates/docker/Dockerfile" Dockerfile
cp "$SKILL_DIR/templates/docker/docker-compose.yml" docker-compose.yml
cp "$SKILL_DIR/templates/docker/docker-compose.dev.yml" docker-compose.dev.yml
```

## Step 7 — Governance docs

```bash
cp "$SKILL_DIR/templates/AGENTS.md" AGENTS.md
cp "$SKILL_DIR/templates/GUIDE.md" GUIDE.md
```

`GUIDE.md` starts with `@AGENTS.md` (Claude Code's file-import syntax) so the
org-wide rules load automatically alongside the project-specific ones.

## Step 8 — Fill in placeholders

Every file below contains `__PROJECT_NAME__` / `__PROJECT_SLUG__` /
`__PROJECT_DESCRIPTION__` / `__DB_NAME__` tokens. Substitute them in one pass —
this uses `python3` instead of `sed -i` because BSD sed (macOS) and GNU sed
(Linux) take that flag differently; this way the command is identical on both:

```bash
PROJECT_NAME="$PROJECT_NAME" PROJECT_SLUG="$PROJECT_SLUG" \
PROJECT_DESCRIPTION="$PROJECT_DESCRIPTION" DB_NAME="$DB_NAME" \
python3 - <<'PY'
import os, pathlib

files = [
    "pyproject.toml", "README.md", "GUIDE.md",
    "app/main.py", "app/middleware/log.py",
    ".env.example", "docker-compose.yml", "docker-compose.dev.yml",
]
tokens = ["PROJECT_NAME", "PROJECT_SLUG", "PROJECT_DESCRIPTION", "DB_NAME"]

for f in files:
    p = pathlib.Path(f)
    text = p.read_text()
    for key in tokens:
        text = text.replace(f"__{key}__", os.environ[key])
    p.write_text(text)
PY
```

## Step 9 — Install dependencies and set up Alembic

```bash
uv sync   # first sync: creates uv.lock from the pyproject.toml we just copied in
          # (no --frozen here — that flag requires an existing lock to match against)

uv run alembic init -t async alembic   # real tool, async template (engine/session boilerplate)
cp "$SKILL_DIR/templates/alembic/env.py" alembic/env.py   # patched: settings-driven URL + target_metadata
```

`alembic.ini`'s generated `sqlalchemy.url` placeholder line is fine as-is —
`env.py` overrides it from `app.core.config.settings.DATABASE_URL` at runtime.

## Step 10 — Local git hooks (optional but recommended)

```bash
uv tool run pre-commit install
```

## Step 11 — Verify (best-effort; skip if Docker isn't available)

`docker-compose.dev.yml` bundles its own Postgres (mapped to host port `5433`,
not `5432`, specifically so it doesn't collide with a Postgres you might
already have running locally) — bring the whole stack up rather than assuming
anything about what else is installed:

```bash
cp .env.example .env
# fill in SECRET_KEY in .env with any random string before continuing, e.g.:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

docker compose -f docker-compose.dev.yml up -d --build
sleep 3   # db healthy + api's own (no-op, no migrations exist yet) startup

# Generate the first migration from the host, against the dev-compose Postgres's
# host-mapped port (5433) -- the api container itself talks to it internally as
# db:5432, which isn't reachable from outside the compose network:
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/$DB_NAME" \
  uv run alembic revision --autogenerate -m "create item table"
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/$DB_NAME" \
  uv run alembic upgrade head

uv run ruff check --fix app/ && uv run ruff format app/
uv run pytest

curl -fsS http://localhost:8000/health/live && echo
curl -fsS http://localhost:8000/health/ready && echo
curl -fsS http://localhost:8000/items && echo

docker compose -f docker-compose.dev.yml down
```

(`uv run pytest`/`ruff` above run on the host, so Step 9's `uv sync` must have
already happened in this same directory — it has, by this point in the runbook.)

If this all passes: migrations run cleanly against a real Postgres, lint/format
are clean, tests pass, and both health endpoints (plus the example `/items`
resource) respond on a live server — the scaffold is a working repo, proven by
actually running it, not just a pile of files that look right.

## Step 12 — Tell the user how to remove the example resource

`item` (routes/controllers/models/schemas/tests) and the migration Step 11
generated for it are only a working example proving the scaffold runs
end-to-end — not something every project needs. Once scaffolding is done, tell
the user this example exists and how to remove it when they're ready to build
their own resources; the exact commands are documented in the generated repo's
`README.md` ("Example resource" section) so they aren't lost after this
conversation ends. Offer to run them now if the user wants a clean slate
immediately — otherwise leave the example in place:

```bash
# Roll back and delete the example migration so alembic's history starts clean
uv run alembic downgrade base
rm -f alembic/versions/*.py

# Remove the example resource's files
rm -f app/models/item.py app/schemas/item.py app/controllers/item.py \
      app/routes/items.py tests/test_items.py

# Drop the now-dangling import/router wiring in app/main.py
python3 - <<'PY'
import pathlib
p = pathlib.Path("app/main.py")
text = p.read_text()
text = text.replace("from app.routes.items import router as items_router\n", "")
text = text.replace('app.include_router(items_router, tags=["Items"])\n', "")
p.write_text(text)
PY
```

After this, `alembic/versions/` is empty again — the next
`alembic revision --autogenerate -m "..."` starts from a blank schema, driven
by whatever real models get added under `app/models/`.

## Step 13 — Wrap up: git remote, commit, push

Ask the user — don't do any of this silently, matching the guardrails above:

- **Remote**: do they want one set now? If so, get the URL and run:
  ```bash
  git remote add origin <url>
  ```
- **Commit**: do they want the initial scaffold committed? If so:
  ```bash
  git add -A
  git commit -m "Initial scaffold via scaffold-fastapi"
  ```
- **Push**: only if they explicitly ask for it, and only once a remote exists:
  ```bash
  git push -u origin main
  ```

## What you get

```
app/
├── main.py                # FastAPI app: lifespan, Sentry, middleware, CORS, exception handlers, routers
├── database.py            # async engine, session maker, Base, get_db dependency (one session per request)
├── core/
│   ├── config.py          # pydantic-settings, reads .env
│   ├── security.py        # JWT create/decode + get_current_user dependency
│   ├── exception_handler.py  # generic error envelope (success/details/data) + logging
│   └── client_ip.py        # X-Forwarded-For aware client IP extraction
├── middleware/             # structured JSON request/response logging
├── models/, schemas/, controllers/, routes/, services/
│   └── item example wired end-to-end across all five (Step 12 removes it)
alembic/                   # async migrations, settings-driven
tests/                     # conftest.py (env bootstrap + shared `client` fixture), health + item tests
.vscode/, .github/, docker-compose.yml, docker-compose.dev.yml, Dockerfile, .env.example, ...
```
