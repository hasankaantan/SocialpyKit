set shell := ["bash", "-cu"]

default: test

# --- backend ---------------------------------------------------------------

dev:
    uv run uvicorn app.main:app --reload

lint:
    uv run ruff check app tests
    uv run ruff format --check app tests

format:
    uv run ruff format app tests
    uv run ruff check --fix app tests

types:
    uv run mypy app tests
    uv run pyright app tests

test-unit:
    uv run pytest tests/unit

test-int:
    uv run pytest tests/integration

test: lint types
    uv run pytest

migrate:
    uv run alembic upgrade head

makemig msg:
    uv run alembic revision --autogenerate -m "{{msg}}"

# Promote an existing user (looked up by email) to the admin role.
# Bootstrap pattern: register the very first account through the api,
# then run `just promote-admin you@example.com` so it can manage the
# rest of the system through the dashboard.
promote-admin email:
    PYTHONPATH=. uv run python scripts/promote_admin.py {{email}}

# --- frontend (ui/) --------------------------------------------------------

ui-install:
    cd ui && bun install

ui-dev:
    cd ui && bun run dev

ui-build:
    cd ui && bun run build

ui-lint:
    cd ui && bun run lint
    cd ui && bun run format:check

ui-format:
    cd ui && bun run format
    cd ui && bun run lint:fix

ui-types:
    cd ui && bun run types

ui-test: ui-lint ui-types
    cd ui && bun run build

# Regenerate ui/openapi.json from the live FastAPI app, then refresh
# ui/src/api/schema.ts. Run after any backend route or schema change.
ui-gen-api:
    uv run python -c "import json; from app.core.server import get_app; print(json.dumps(get_app().openapi(), indent=2))" > ui/openapi.json
    cd ui && bun run gen-api

# --- monorepo --------------------------------------------------------------

test-all: test ui-test
