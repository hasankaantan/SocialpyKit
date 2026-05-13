# SocialpyKit

[![Backend CI](https://github.com/hasankaantan/SocialpyKit/actions/workflows/tests.yml/badge.svg)](https://github.com/hasankaantan/SocialpyKit/actions/workflows/tests.yml)
[![Frontend CI](https://github.com/hasankaantan/SocialpyKit/actions/workflows/frontend.yml/badge.svg)](https://github.com/hasankaantan/SocialpyKit/actions/workflows/frontend.yml)
[![License: MIT](https://img.shields.io/github/license/hasankaantan/SocialpyKit?color=blue)](./LICENSE)
[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/downloads/)
[![Type checked: mypy + pyright](https://img.shields.io/badge/type%20checked-mypy%20%2B%20pyright-blue)](https://github.com/python/mypy)
[![Linter: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Coverage: 100%](https://img.shields.io/badge/coverage-100%25-brightgreen)](./tests)
[![Template repo](https://img.shields.io/badge/template-use_this_template-success)](https://github.com/hasankaantan/SocialpyKit/generate)

> FastAPI starter kit — strict types, immutable schemas, async SQLAlchemy, 100% coverage gate. Python's answer to [nunomaduro/laravel-starter-kit](https://github.com/nunomaduro/laravel-starter-kit). Phased build, Conventional Commits.

Production-grade FastAPI starter engineered by **Socialbug Apps LLC**. Built on top of [s3rius/FastAPI-template](https://github.com/s3rius/FastAPI-template) and layered with a services / repositories architecture, ultra-strict tooling, and a fail-fast philosophy.

If `nunomaduro/laravel-starter-kit` set the bar for "what a senior-grade Laravel starter should look like", **SocialpyKit aims for the same bar in Python**: every default is opinionated, type-safe, and refuses to ship sloppy code.

---

## Table of Contents

- [Highlights](#highlights)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Using This Template](#using-this-template)
- [Quick Start](#quick-start)
- [Development Workflow](#development-workflow)
- [Strict Tooling Principles](#strict-tooling-principles)
- [Build Phases](#build-phases)
- [Configuration](#configuration)
- [Testing](#testing)
- [Migrations](#migrations)
- [Contributing](#contributing)
- [References](#references)
- [License](#license)

---

## Highlights

- **100% type coverage** — every function, method, parameter, return type, and attribute is explicitly typed. No implicit `Any`, no bare `dict` / `list`.
- **Two type checkers, both strict** — `mypy --strict` *and* `pyright --strict` must pass with zero errors.
- **Ruff at maximum strictness** — `select = ["ALL"]`. The very short ignore list is documented per rule.
- **Immutable-first DTOs** — Pydantic v2 `BaseSchema` is `frozen=True`, rejects `extra` fields, strips whitespace at the boundary.
- **Services / repositories architecture** — routers depend on services, services depend on `BaseRepository` ABCs, never on SQLAlchemy directly.
- **Async everywhere** — async route handlers, async SQLAlchemy 2.0 with `asyncpg`, async fixtures, `httpx.AsyncClient` for tests.
- **No lazy loading** — eager-load every relationship explicitly (`selectinload` / `joinedload`).
- **100% test coverage** — `--cov-fail-under=100` enforced in CI from Phase 3.4 onward.
- **Conventional Commits, atomic history** — every commit is one logical change, written in the project's documented style.
- **No AI attribution** — commits never reference Claude / Copilot / "Generated with" footers.

---

## Tech Stack

| Layer | Choice |
|-------|--------|
| Language | Python 3.13+ |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (async, `Mapped[T]` / `mapped_column`) |
| Validation | Pydantic v2 (`frozen`, `extra="forbid"`) |
| Migrations | Alembic |
| Database | PostgreSQL (`asyncpg`) |
| Auth | JWT (`passlib` + `bcrypt`) |
| Observability | Sentry SDK |
| Runtime | Gunicorn + Uvicorn workers |
| Dates | `whenever` (no `datetime.now()` / `utcnow()`) |
| Logging | `loguru` (no bare `print()`) |
| Package manager | `uv` |
| Lint / format | `ruff` |
| Type checking | `mypy` + `pyright` (both strict) |
| Tests | `pytest`, `pytest-asyncio`, `pytest-cov`, `httpx` |
| Task runner | `just` |
| Pre-commit | `pre-commit` |
| CI | GitHub Actions |
| Frontend (`ui/` in this monorepo) | Vue 3 + Vite + Pinia + Axios + `openapi-typescript`, managed with `bun` |

---

## Architecture

```
app/
  api/
    v1/
      routers/        # one file per domain — call services only
      dependencies/   # FastAPI Depends() helpers
  core/
    config.py         # pydantic-settings Settings
    security.py       # JWT, password hashing
    essentials.py     # BaseModel, BaseSchema, BaseRepository ABCs
    exceptions.py     # custom exception hierarchy
    logging.py        # loguru setup
  models/             # SQLAlchemy ORM models (Mapped[T])
  schemas/            # Pydantic v2 DTOs (frozen, separate Request / Response)
  services/           # business logic, framework-agnostic
  repositories/       # data access, SQLAlchemy queries only
  db/
    session.py        # async engine + session factory
    base.py           # DeclarativeBase
migrations/           # Alembic — never edit manually
tests/
  unit/               # services and pure logic
  integration/        # DB + API tests via httpx.AsyncClient
  conftest.py
ui/                   # Vue 3 frontend (monorepo, bun-managed)
  src/
    api/              # openapi-typescript generated types + axios wrappers
    components/       # .vue components
    main.ts
  package.json
  vite.config.ts
  eslint.config.ts
  openapi.json        # exported from backend, regenerate via `just ui-gen-api`
justfile              # all commands (backend, frontend, monorepo)
pyproject.toml        # all backend tool config (ruff, mypy, pyright, pytest, coverage)
.pre-commit-config.yaml
CLAUDE.md             # AI assistant guardrails (read this before contributing)
AGENTS.md
```

### Layer Rules

| From → To | Allowed | Forbidden |
|-----------|---------|-----------|
| Router → Service | ✅ | — |
| Router → Repository | ❌ | direct repository access |
| Router → Model | ❌ | direct ORM access |
| Service → Repository (interface) | ✅ | — |
| Service → FastAPI primitives | ❌ | services stay framework-agnostic |
| Repository → SQLAlchemy | ✅ | — |
| Repository → business logic | ❌ | only data access |
| Schema → Schema | DTO is `frozen=True`; never reuse the same schema for input *and* output | — |

---

## Using This Template

There are two ways to start a new project from SocialpyKit:

### Option A — GitHub "Use this template" (one click)

The repo is registered as a [GitHub template repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository). Click **Use this template → Create a new repository** on the GitHub UI to clone the source tree verbatim into a fresh repo under your own account.

After cloning, run the rename script with your project name, display name, and GitHub org:

```bash
./scripts/rename-project.sh myapi "My API" my-org
```

The script (`scripts/rename-project.sh`) walks the tree with `git grep` and rewrites every project literal in one pass — env-var prefix, db name, docker image, display name, github org. Review the diff, then commit:

```bash
git diff                         # sanity check
git add -A && git commit -m "chore: rename project from socialpykit"
```

Manual follow-up after the script runs (the script prints these too):

- Update `[project].authors` and `maintainers` in `pyproject.toml`.
- Update the copyright holder in `LICENSE`.
- Set your Sentry DSN env var (e.g. `MYAPI_SENTRY_DSN=...`).
- Regenerate ui types if you touched the API: `just ui-gen-api`.
- Recreate the dev database so the new credentials take effect: `docker compose down -v && docker compose up -d db`.

### Option B — Copier (parametrised, recommended for new automation)

`copier.yaml` declares the variables a future copier render would prompt for (project name, slug, author, sentry toggle, etc.). The source tree is **not yet parametrised** with Jinja, so `copier copy` against `main` is the same as Option A for now. Once the `template` branch ships, you'll be able to:

```bash
uvx copier copy gh:hasankaantan/socialpykit@template ./my-new-service
```

Until then, prefer Option A.

---

## Quick Start

### Prerequisites

- Python 3.13+ (managed via `.python-version`)
- `uv` ≥ 0.11
- `just` ≥ 1.51 — `brew install just` or [casey/just releases](https://github.com/casey/just)
- Docker + Docker Compose (for the dev database)

### Setup

```bash
git clone git@github.com:hasankaantan/socialpykit.git
cd socialpykit

# --- backend ---
uv sync                        # install python deps into .venv
uv run pre-commit install      # install git hooks
docker compose up -d db        # start the dev database
just migrate                   # run alembic upgrade head
just dev                       # boot uvicorn with reload

# --- frontend (in a second terminal) ---
just ui-install                # install bun deps inside ui/
just ui-dev                    # boot vite with hmr
```

- Backend API: `http://localhost:8000`. Swagger UI at `/api/docs`, ReDoc at `/api/redoc`.
- Frontend dev server: `http://localhost:5173` (Vite default).
- Frontend reads the API via `VITE_API_BASE_URL` (defaults to `http://localhost:8000`).

---

## Development Workflow

Every command lives in the [`justfile`](./justfile):

```bash
# --- backend ---
just dev            # uvicorn with reload
just lint           # ruff check + ruff format --check
just format         # ruff format + ruff check --fix
just types          # mypy --strict + pyright --strict
just test-unit      # pytest tests/unit
just test-int       # pytest tests/integration
just test           # lint + types + full pytest run
just migrate        # alembic upgrade head
just makemig msg="…" # alembic revision --autogenerate -m "…"

# --- frontend (ui/) ---
just ui-install     # bun install inside ui/
just ui-dev         # vite dev server with hmr
just ui-build       # vue-tsc + vite build
just ui-lint        # eslint + prettier --check
just ui-format      # prettier --write + eslint --fix
just ui-types       # vue-tsc --noEmit
just ui-test        # ui-lint + ui-types + ui-build (full frontend pipeline)
just ui-gen-api     # regenerate ui/openapi.json + ui/src/api/schema.ts

# --- monorepo ---
just test-all       # just test && just ui-test  ← run before every commit
```

**Rule of thumb:** if `just test-all` is red, the branch is not mergeable.

---

## Strict Tooling Principles

These are non-negotiable. Every PR is judged against them.

1. **100% type coverage.** Every function, method, parameter, return, and attribute is typed.
2. **mypy strict + pyright strict.** Both pass with zero errors.
3. **Ruff `select = ["ALL"]`.** Ignores are documented per rule.
4. **Immutable-first.** Pydantic DTOs are `frozen=True`, with `extra="forbid"`. Prefer `tuple` over `list` for fixed collections. Use `Final[T]` for module-level constants.
5. **Fail-fast.** Validate at boundaries via Pydantic. Never pass raw `dict` across layers. Raise early. Never swallow exceptions silently.
6. **100% test coverage.** From Phase 3.4 onward, `pytest --cov-fail-under=100`.
7. **DRY + SOLID.** Shared logic in services / core utilities. Depend on abstractions (`BaseRepository`), not concretions.
8. **Async by default.** All route handlers and repository methods are `async def`.
9. **`whenever` for dates.** Never `datetime.now()` or `datetime.utcnow()`.
10. **`loguru` for logs.** Never `print()`.
11. **`Depends()` for DI.** Never instantiate services or repositories manually inside routers.
12. **`pydantic-settings` for config.** No scattered `os.environ.get()`.
13. **Alembic for every schema change.** Never `Base.metadata.create_all()` in production code paths.
14. **Eager loading explicitly.** `selectinload` / `joinedload` for every relationship — never lazy.

---

## Build Phases

SocialpyKit is built in deliberate phases. Each step within a phase is its own commit (Conventional Commits, present tense, no AI attribution).

| Phase | Status | Scope |
|-------|--------|-------|
| **Phase 0** — Base template | ✅ Done | `fastapi_template` scaffold, cleanup, Python 3.13 pin |
| **Phase 1** — Tooling | ✅ Done | Strict `pyproject.toml`, `justfile`, pre-commit, pipeline verification |
| **Phase 2** — Architecture refactor | 🚧 In progress | `essentials.py`, exception hierarchy, services / repositories, `whenever` migration |
| **Phase 3** — Test & coverage | ⏳ | Shared fixtures, unit + integration suites, 100% coverage gate |
| **Phase 4** — AI / dev experience | ⏳ | `CLAUDE.md` ✅, `AGENTS.md`, `.mcp.json`, `.cursor/` rules |
| **Phase 5** — Vue 3 frontend (monorepo `ui/`) | ✅ Done | Vite + Pinia + Axios + `openapi-typescript`, bun-managed, ESLint strict |
| **Phase 6** — Template parameterization | ✅ Done (soft) | `copier.yaml` variables, repo marked as GitHub template, `scripts/rename-project.sh` automates the rename |

For the detailed phase-by-phase commit plan, see [`CLAUDE.md`](./CLAUDE.md).

---

## Configuration

Configuration is driven by environment variables, parsed via `pydantic-settings`. All variables use the `SOCIALPYKIT_` prefix.

Example `.env` (do not commit this — it is `.gitignore`d):

```bash
SOCIALPYKIT_RELOAD=True
SOCIALPYKIT_HOST=0.0.0.0
SOCIALPYKIT_PORT=8000
SOCIALPYKIT_ENVIRONMENT=dev
SOCIALPYKIT_DB_HOST=localhost
SOCIALPYKIT_DB_PORT=5432
SOCIALPYKIT_DB_USER=socialpykit
SOCIALPYKIT_DB_PASS=socialpykit
SOCIALPYKIT_DB_BASE=socialpykit
SOCIALPYKIT_SENTRY_DSN=

# JWT — see warning below
SOCIALPYKIT_JWT_SECRET_KEY=replace-this-in-production
SOCIALPYKIT_JWT_ALGORITHM=HS256
SOCIALPYKIT_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Every Settings field is reflected as `SOCIALPYKIT_<UPPERCASE_FIELD>`. See [`app/settings.py`](./app/settings.py) for the full surface.

> ⚠️ **`SOCIALPYKIT_JWT_SECRET_KEY` is required in production.** The default
> value in `app/settings.py` is the literal string `dev-only-do-not-use-in-production`
> and it ships intentionally weak so a forgotten override is immediately obvious.
> Generate a strong key once per environment:
>
> ```bash
> python -c "import secrets; print(secrets.token_urlsafe(64))"
> ```
>
> Set it via your deployment platform's secret manager — never commit it.

---

## Testing

Tests run against a **real** PostgreSQL instance. We do not mock the database in integration tests — production parity matters more than test startup time.

```bash
# start the test database (or reuse the dev one)
docker compose up -d db

# fast loop
just test

# layered targets (after Phase 3)
just test-unit
just test-int
```

Integration tests use `httpx.AsyncClient` + `ASGITransport`. The session-scoped `_engine` fixture creates and drops a dedicated `socialpykit_test` database per test session; each test gets its own `dbsession` with a SAVEPOINT-style rollback.

---

## Migrations

```bash
just migrate                 # apply all pending migrations
just makemig msg="add users" # autogenerate a new revision
```

Under the hood:

```bash
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "…"
uv run alembic downgrade <revision_id>
uv run alembic downgrade base
```

**Never** edit migrations under `app/db/migrations/versions/` by hand. Always regenerate with `--autogenerate`.

---

## Contributing

Contributions are welcome — and held to the same bar as internal work.

1. **Read [`CLAUDE.md`](./CLAUDE.md) first.** It documents every guardrail.
2. **Branch from `main`.** Name it `feat/<thing>`, `fix/<thing>`, `chore/<thing>`, etc.
3. **One logical change per commit.** Use [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` new feature
   - `fix:` bug fix
   - `chore:` build / tooling
   - `refactor:` no behaviour change
   - `test:` tests only
   - `docs:` documentation
   - `ci:` GitHub Actions
4. **Present tense, lowercase, ≤ 72 chars on the first line.** Body wraps at 72.
5. **No AI attribution.** Do not add `Co-Authored-By: Claude` or "Generated with X" footers.
6. **`just test` must pass.** Lint, both type checkers, and pytest — all green before opening a PR.
7. **Touch only what the change requires.** Bug fixes are not refactor opportunities. If you spot adjacent dead code, mention it in the PR description; do not silently rewrite it.
8. **No `# type: ignore` without a specific rule code and explanation.** Same for `# noqa`.
9. **No `print()`.** Use `loguru.logger`.
10. **No `datetime.now()` / `datetime.utcnow()`.** Use `whenever`.

PRs that ignore these rules will be sent back. PRs that follow them tend to merge fast.

---

## References

| Repo | Why it's referenced |
|------|---------------------|
| [nunomaduro/laravel-starter-kit](https://github.com/nunomaduro/laravel-starter-kit) | Inspiration — every strictness principle is adapted from here |
| [nunomaduro/laravel-starter-kit-inertia-vue](https://github.com/nunomaduro/laravel-starter-kit-inertia-vue) | Frontend architecture reference |
| [s3rius/FastAPI-template](https://github.com/s3rius/FastAPI-template) | Base template the project is generated from |
| [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) | Official FastAPI full-stack reference |
| [zhanymkanov/fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices) | FastAPI best-practices guide |
| [nunomaduro/essentials](https://github.com/nunomaduro/essentials) | Laravel Essentials — Python equivalent lives in `app/core/essentials.py` |

---

## License

MIT — see [`LICENSE`](./LICENSE). Copyright © 2026 Socialbug Apps LLC.

---

## Maintainers

**Socialbug Apps LLC** — Hasan Kaan Tan ([@hasankaantan](https://github.com/hasankaantan))

Stack lead: Laravel → FastAPI migration. Standards: PHPStan-equivalent strictness, Pest-equivalent coverage, SOLID, DRY, Conventional Commits.
