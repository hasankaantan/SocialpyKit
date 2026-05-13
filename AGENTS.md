# AGENTS.md

Agent-facing instructions for SocialpyKit. Tooling-agnostic — applies to OpenAI Codex CLI, Cursor, Aider, or any other AI coding assistant. For the extended Claude-specific guardrails, read [`CLAUDE.md`](./CLAUDE.md).

## Project

SocialpyKit is a production-grade FastAPI starter kit. Stack: Python 3.13+, FastAPI, SQLAlchemy 2.0 async, Pydantic v2, PostgreSQL, JWT auth. Architecture: services / repositories with strict typing and immutable DTOs.

## Setup commands

```bash
uv sync                       # install dependencies
uv run pre-commit install     # install git hooks
docker compose up -d db       # start the test postgres
just migrate                  # apply migrations
```

## Development commands

```bash
just dev          # uvicorn with reload
just lint         # ruff check + ruff format --check
just format       # ruff format + ruff check --fix
just types        # mypy --strict + pyright --strict
just test         # lint + types + pytest (full pipeline)
just test-unit    # tests/unit only
just test-int     # tests/integration only
just migrate      # alembic upgrade head
just makemig msg="…"  # alembic revision --autogenerate -m "…"
```

`just test` must be green before any commit.

## Code style rules

- **100% type coverage.** Every function, method, parameter, return, attribute.
- **mypy --strict and pyright --strict both pass with zero errors.**
- **Ruff `select = ["ALL"]`.** Per-rule ignores are documented in `pyproject.toml`.
- **Pydantic v2 DTOs are immutable.** Use `BaseSchema` from `app.core.essentials` — `frozen=True`, `extra="forbid"`, `from_attributes=True`.
- **Services are framework-agnostic.** No FastAPI imports inside `app/services/`.
- **Repositories implement `BaseRepository`.** No business logic in `app/repositories/`.
- **Routers only call services.** Never touch repositories or ORM models directly.
- **Async by default.** Every route handler and every repository method is `async def`.
- **Eager loading only.** `lazy="raise"` is the default via the `relationship` wrapper in `app/db/base.py`. Opt into `selectinload` / `joinedload` explicitly.
- **`whenever` for dates.** Never `datetime.now()` / `datetime.utcnow()`.
- **`loguru.logger`.** Never bare `print()`.
- **`pydantic-settings`.** Never scattered `os.environ.get()`.
- **No `# type: ignore` without a specific rule code and explanation.** Same for `# noqa` and `# pragma: no cover`.
- **No mutable default arguments.** Use `None` plus an explicit check or `field(default_factory=...)`.
- **No bare `except`.** Always catch specific exceptions.
- **`Depends()` for DI.** Never instantiate services or repositories manually inside routers.

## Architecture

```
app/
  core/         essentials (BaseModel, BaseSchema, BaseRepository), exceptions
  models/       SQLAlchemy ORM (Mapped[T], mapped_column)
  schemas/      Pydantic DTOs (frozen, separate Request / Response)
  services/     business logic, framework-agnostic
  repositories/ data access, SQLAlchemy queries only
  db/           session factory, declarative base
  web/          FastAPI app factory, lifespan, router mounting
  api/v1/       routers and dependencies (target layout, in progress)
```

## Testing rules

- **No mocking the database in integration tests.** Use the real test PostgreSQL via `dbsession` fixture.
- **Mock only external services** (HTTP calls, Sentry, email providers).
- **`httpx.AsyncClient` + `ASGITransport`** for endpoint tests, never `TestClient`.
- **Unit tests** go in `tests/unit/` and use in-memory fakes that inherit the real repository class.
- **Integration tests** go in `tests/integration/` and drive the FastAPI app end to end.
- **Shared fixtures live in `tests/conftest.py`.** Do not duplicate fixtures inside test files.
- **100% line coverage is enforced.** Use `# pragma: no cover` only on truly production-only paths.

## Security rules

- JWT only (no session cookies).
- Passwords hashed with `bcrypt` via `passlib`.
- Never log sensitive fields (passwords, tokens, PII).
- All endpoints require explicit auth dependency unless explicitly public.
- CORS configured explicitly. No `allow_origins=["*"]` in production.

## Commit rules

- Conventional Commits: `feat:`, `fix:`, `chore:`, `refactor:`, `test:`, `docs:`, `ci:`.
- Simple present tense lowercase: `feat: adds user authentication`, not `feat: add` or `Added`.
- First line ≤ 72 characters. Body wraps at 72.
- One logical change per commit.
- **Never mention AI, Claude, Copilot, Codex, Cursor, or any LLM in commit messages or code comments.** No `Co-Authored-By: <model>` footer, no "Generated with" tag.

## What NOT to do

- Do not add `# type: ignore` without a specific rule and explanation.
- Do not create synchronous route handlers or repository methods.
- Do not use `dict` as a function parameter or return type — define a schema.
- Do not skip tests for new code.
- Do not use `datetime.now()`.
- Do not write business logic in routers.
- Do not write SQLAlchemy queries in services.
- Do not use `print()`.
- Do not edit migration files manually — always `alembic revision --autogenerate`.
- Do not bypass `just test` before committing.

## Build phases

The repository is built in phases (see [`CLAUDE.md`](./CLAUDE.md) for the full plan and current status). When in doubt about scope, prefer the smaller commit that completes one phase step.
