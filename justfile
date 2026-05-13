set shell := ["bash", "-cu"]

default: test

# --- backend ---------------------------------------------------------------

dev:
    uv run uvicorn app.web.application:get_app --reload --factory

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
    uv run python -c "import json; from app.web.application import get_app; print(json.dumps(get_app().openapi(), indent=2))" > ui/openapi.json
    cd ui && bun run gen-api

# --- monorepo --------------------------------------------------------------

test-all: test ui-test
