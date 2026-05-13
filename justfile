set shell := ["bash", "-cu"]

default: test

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
