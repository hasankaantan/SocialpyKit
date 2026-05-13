# SocialpyKit — Claude Code Instructions

## Project Overview

**SocialpyKit** is a production-grade FastAPI starter kit engineered by Socialbug Apps LLC.
It is the Python/FastAPI equivalent of `nunomaduro/laravel-starter-kit` — ultra-strict, type-safe,
immutable-first, fail-fast. Base: `s3rius/FastAPI-template` (postgresql + sqlalchemy 2.0 +
alembic + jwt-auth + sentry + gunicorn + github-ci), layered with strict tooling and
a services/repositories architecture.

## Reference Repositories

| Repo | Rol |
|------|-----|
| [nunomaduro/laravel-starter-kit](https://github.com/nunomaduro/laravel-starter-kit) | İlham kaynağı — tüm sıkılık prensipleri buradan adapte edildi |
| [nunomaduro/laravel-starter-kit-inertia-vue](https://github.com/nunomaduro/laravel-starter-kit-inertia-vue) | Frontend mimarisi referansı |
| [s3rius/FastAPI-template](https://github.com/s3rius/FastAPI-template) | Base template — projenin iskelet kaynağı |
| [fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) | Resmi FastAPI full-stack referansı (mimari kararlar için) |
| [zhanymkanov/fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices) | FastAPI best practices rehberi (8k+ yıldız) |
| [nunomaduro/essentials](https://github.com/nunomaduro/essentials) | Laravel Essentials — Python karşılığı `app/core/essentials.py` olarak implement edildi |

**Stack:** Python 3.13+ · FastAPI · SQLAlchemy 2.0 (async) · Alembic · Pydantic v2 · PostgreSQL
**Tooling:** uv · ruff · mypy (strict) · pyright (strict) · pytest · pytest-cov · pre-commit · just
**Frontend (monorepo, `ui/` directory):** Vue 3 · Vite · Pinia · Axios · openapi-typescript · bun · ESLint · Prettier · vue-tsc

---

## Core Principles (Non-Negotiable)

1. **100% type coverage** — every function, method, parameter, return type, and class attribute
   must be explicitly typed. No implicit `Any`. No bare `dict` or `list` without type params.
2. **mypy strict + pyright strict** — both must pass with zero errors/warnings.
3. **ruff at maximum strictness** — all selected rules must pass. No `# noqa` without
   a specific rule code and a comment explaining why.
4. **Immutable-first** — Pydantic models use `model_config = ConfigDict(frozen=True)`.
   Use `Final[T]` for constants. Prefer `tuple` over `list` for fixed collections.
5. **Fail-fast** — validate at boundaries (API layer via Pydantic). Never pass raw dicts
   across layer boundaries. Raise early, never swallow exceptions silently.
6. **100% test coverage** — `pytest --cov=app --cov-fail-under=100`. No untested code ships.
7. **DRY** — shared logic lives in services or core utilities. Never duplicate business logic.
8. **SOLID** — single responsibility per class/function, depend on abstractions (ABCs), not concretions.

---

## Commit Rules

- Follow **Conventional Commits**: `feat:`, `fix:`, `chore:`, `refactor:`, `test:`, `docs:`, `ci:`
- **Never mention AI, Claude, or any LLM in commit messages or code comments.**
- Keep commits atomic and focused. One logical change per commit.

---

## Architecture

```
app/
  api/
    v1/
      routers/        # One file per domain (users.py, auth.py, ...)
      dependencies/   # FastAPI Depends() functions
  core/
    config.py         # pydantic-settings, Settings class
    security.py       # JWT, password hashing
    essentials.py     # BaseModel, BaseSchema, BaseRepository ABCs
    exceptions.py     # Custom exception hierarchy
    logging.py        # Loguru configuration
  models/             # SQLAlchemy ORM models (one file per domain)
  schemas/            # Pydantic v2 schemas (Request/Response, frozen=True)
  services/           # Business logic (one class per domain)
  repositories/       # Data access (one class per domain, depends on ABCs)
  db/
    session.py        # Async engine + session factory
    base.py           # DeclarativeBase
migrations/           # Alembic (never edit manually, use alembic commands)
tests/
  unit/               # Pure logic tests (services, utils)
  integration/        # DB + API tests (pytest-asyncio + httpx AsyncClient)
  conftest.py         # Shared fixtures
ui/                   # Vue 3 frontend (monorepo, see ### Frontend below)
  src/
    api/              # Generated openapi-typescript types + axios client
    components/       # Vue SFCs
    main.ts
  package.json        # bun-managed deps
  vite.config.ts
  eslint.config.ts    # flat config, strict type-checked
  .prettierrc.json
  openapi.json        # exported from backend, source of truth for ui types
justfile              # All commands (test, lint, format, migrate, ui-*, ...)
pyproject.toml        # All backend tool config (ruff, mypy, pytest, coverage)
.pre-commit-config.yaml
CLAUDE.md
AGENTS.md
.mcp.json
```

### Frontend (`ui/` directory)

The frontend is **not a separate repo** — it lives in `ui/` inside this monorepo. Rationale: keeping backend and frontend in lockstep removes the OpenAPI sync problem (single PR can change both layers and regenerate `ui/src/api/schema.ts` with `just ui-gen-api`).

Conventions:

- **Package manager:** `bun` (lockfile is `bun.lock`).
- **Type safety:** every API call goes through the generated `paths` interface in `ui/src/api/schema.ts`. Domain endpoints live in `ui/src/api/endpoints/<domain>.ts` as typed wrappers; no untyped `http.get(url)` in the rest of the codebase.
- **Lint / format:** `eslint.config.ts` uses `eslint-plugin-vue` flat/recommended + `vueTsConfigs.recommendedTypeChecked` (strict type-aware rules) + prettier skip-formatting layer. Prettier owns formatting; ESLint does not enforce it.
- **Type check:** `vue-tsc --noEmit` must pass with zero errors.
- **No build-time fetch of OpenAPI.** `ui/openapi.json` is committed; regenerate explicitly with `just ui-gen-api` after backend route or schema changes.
- **No `any`.** Same rule as the backend's mypy strict — applies to TypeScript too.

Just recipes wrap every command: `just ui-install`, `just ui-dev`, `just ui-build`, `just ui-lint`, `just ui-format`, `just ui-types`, `just ui-test`, `just ui-gen-api`. `just test-all` runs both backend and frontend pipelines.

### Layer Rules

- **Routers** → call Services only. Never touch repositories or models directly.
- **Services** → contain all business logic. Call Repositories for data access.
  Never import FastAPI (Request, Depends, etc.) — services are framework-agnostic.
- **Repositories** → only SQLAlchemy queries. No business logic. Return domain models or
  typed DTOs, never raw SQLAlchemy Row objects.
- **Schemas** → Pydantic v2, always `frozen=True`. Separate Request and Response schemas.
  Never reuse the same schema for input and output.
- **Models** → SQLAlchemy 2.0 mapped classes. Use `Mapped[T]` and `mapped_column()` only.
  No legacy `Column()` style.

---

## Tooling Configuration Summary

### pyproject.toml expectations

```toml
[tool.mypy]
strict = true
warn_unreachable = true
warn_unused_ignores = true
disallow_any_generics = true
disallow_any_unimported = true

[tool.pyright]
typeCheckingMode = "strict"
reportMissingTypeStubs = false

[tool.ruff]
target-version = "py313"
line-length = 88

[tool.ruff.lint]
select = ["ALL"]
ignore = [
  "D",      # docstrings optional (add back if project needs them)
  "ANN101", # self type annotation
  "ANN102", # cls type annotation
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
addopts = "--cov=app --cov-fail-under=100 --cov-report=term-missing"

[tool.coverage.report]
exclude_lines = [
  "pragma: no cover",
  "if TYPE_CHECKING:",
  "@overload",
  "raise NotImplementedError",
]
```

### justfile commands

```
just lint        # ruff check + ruff format --check
just format      # ruff format + ruff check --fix
just types       # mypy --strict + pyright
just test:unit   # pytest tests/unit
just test:int    # pytest tests/integration
just test        # lint + types + all tests (full pipeline, must pass before commit)
just migrate     # alembic upgrade head
just makemig msg # alembic revision --autogenerate -m "msg"
just dev         # uvicorn app.main:app --reload
```

---

## Code Style Rules

- **No `Any`** anywhere, except `# type: ignore[assignment]` with explanation if truly unavoidable (rare).
- **No mutable default arguments** — use `None` with explicit check or `field(default_factory=...)`.
- **No bare `except`** — always catch specific exceptions.
- **No `print()`** — use `loguru.logger` everywhere.
- **Async by default** — all route handlers and repository methods must be `async def`.
- **Dependency injection via `Depends()`** — never instantiate services or repositories manually in routers.
- **Environment config via `pydantic-settings`** — no `os.environ.get()` scattered in code.
- **`whenever` for dates** — never use `datetime.now()` or `datetime.utcnow()`. Use `whenever` library.
- **`result` pattern for errors** in service layer when appropriate — avoid exception-as-control-flow.

---

## Database Rules

- **Always use async SQLAlchemy** (`asyncpg` driver).
- **Never use lazy loading** — explicit `selectinload()` or `joinedload()` for every relationship.
- **Alembic for all schema changes** — never `Base.metadata.create_all()` in production paths.
- **Typed columns only** — `Mapped[str]`, `Mapped[int | None]`, etc.

---

## Testing Rules

- Every new service method → unit test in `tests/unit/`.
- Every new endpoint → integration test in `tests/integration/`.
- Use `httpx.AsyncClient` with `ASGITransport` for integration tests — never `TestClient`.
- Fixtures in `conftest.py` — no fixture duplication across test files.
- **No mocking the database** in integration tests — use a real test PostgreSQL instance.
- Mock only external services (HTTP calls, Sentry, email providers).

---

## Security Rules

- **JWT only** — no session cookies (this is an API-first kit).
- Passwords hashed with `bcrypt` via `passlib`.
- Never log sensitive fields (passwords, tokens, PII).
- All endpoints require explicit auth dependency unless decorated with `# public endpoint`.
- CORS configured explicitly — no `allow_origins=["*"]` in production config.

---

## What Claude Code Should NOT Do

- Do not add `# type: ignore` without a specific rule and explanation.
- Do not create synchronous route handlers or repository methods.
- Do not use `dict` as a function parameter or return type — define a schema.
- Do not skip writing tests for new code.
- Do not use `datetime.now()` — always use `whenever`.
- Do not write business logic in routers.
- Do not write SQLAlchemy queries in services.
- Do not mention Claude, AI, or LLMs in any commit message, comment, or documentation.
- Do not use `print()` — use `loguru.logger`.
- Do not generate migration files manually — always use `alembic revision --autogenerate`.

---

## Build Phases

The project is built in phases. Always check current phase before adding features.
**After completing each step within a phase, commit immediately.** Every commit must follow
Conventional Commits format and the rules defined in the Commit Rules section above.
Never bundle multiple steps into one commit.

---

### Faz 0 — Base Template

Steps and commits:

1. Generate s3rius template with: `postgresql · sqlalchemy · alembic · jwt-auth · sentry · gunicorn · github-ci · routers · dummy`
   `chore: initialize project from s3rius/FastAPI-template`

2. Delete unnecessary generated files (unused ORMs, example leftover configs)
   `chore: remove unused generated files from template`

3. Set Python version to 3.13 in `.python-version`
   `chore: set python version to 3.13`

---

### Faz 1 — Tooling ← **CURRENT**

Steps and commits:

1. Configure `pyproject.toml` — ruff, mypy, pyright, pytest, coverage sections
   `chore: add strict tooling config to pyproject.toml`

2. Add `justfile` with all commands (lint, format, types, test, migrate, dev)
   `chore: add justfile with dev and ci commands`

3. Add `.pre-commit-config.yaml` (ruff, mypy, trailing whitespace, end-of-file-fixer)
   `chore: add pre-commit hooks`

4. Verify `just test` passes on generated base
   `chore: verify tooling pipeline passes on base template`

---

### Faz 2 — Architecture Refactor

Steps and commits:

1. Create `app/core/essentials.py` (BaseSchema frozen, BaseModel, BaseRepository ABC)
   `feat: add core essentials with immutable base classes`

2. Create `app/core/exceptions.py` (custom exception hierarchy)
   `feat: add custom exception hierarchy`

3. Add `services/` directory with base structure
   `feat: add services layer skeleton`

4. Add `repositories/` directory with base structure
   `feat: add repositories layer skeleton`

5. Port demo router to services/repositories pattern
   `refactor: port demo router to service-repository architecture`

6. Add SQLAlchemy strict typing + eager loading session hook
   `feat: enforce strict sqlalchemy typing and eager loading`

7. Replace any `datetime.now()` usage with `whenever`
   `refactor: replace datetime usage with whenever library`

---

### Faz 3 — Test & Coverage

Steps and commits:

1. Add `conftest.py` with shared fixtures (async client, db session, test settings)
   `test: add shared fixtures to conftest`

2. Write unit tests for all service methods
   `test: add unit tests for service layer`

3. Write integration tests for all endpoints
   `test: add integration tests for api endpoints`

4. Enforce `--cov-fail-under=100` and verify pipeline passes
   `test: enforce 100 percent coverage threshold`

---

### Faz 4 — AI / Dev Experience

Steps and commits:

1. Add `CLAUDE.md` (this file) to repo root
   `docs: add CLAUDE.md with project conventions`

2. Add `AGENTS.md`
   `docs: add AGENTS.md`

3. Add `.mcp.json` (Sentry MCP)
   `chore: add mcp.json with sentry integration`

4. Add `.cursor/` rules if applicable
   `chore: add cursor rules`

---

### Faz 5 — Vue 3 Frontend (monorepo, `ui/` directory)

Steps and commits:

1. Scaffold Vue 3 + Vite + Pinia + Axios into `ui/`
   `chore: initialize vue3 project with vite and pinia`

2. Generate type-safe API client from FastAPI OpenAPI schema
   `feat: add openapi-typescript generated api client`

3. Configure eslint strict + prettier + vue-tsc strict
   `chore: add strict eslint and typescript config`

4. Add `.github/workflows/frontend.yml` so lint, types, and build run
   on every push and PR touching `ui/`
   `chore: verify frontend type check pipeline`

5. Add `just ui-*` recipes and `just test-all` for the monorepo
   `chore: add frontend recipes to justfile`

6. Document the monorepo layout and ui/ conventions
   `docs: convert layout to monorepo and document ui directory`

---

### Faz 6 — Template Parametrization

Steps and commits:

1. Add `copier.yaml` with project variables (name, description, author, db, features)
   `feat: add copier template configuration`

2. Parametrize all hardcoded project names in files
   `refactor: replace hardcoded project names with copier variables`

3. Add `copier` usage instructions to README
   `docs: add copier usage to readme`

4. Mark repo as GitHub template repository
   `chore: mark repository as github template`

---

## Developer

**Socialbug Apps LLC** — Hasan Kaan Tan
Stack lead: Laravel → FastAPI migration
Standards: PHPStan-equivalent strictness, Pest-equivalent coverage, SOLID, DRY, Conventional Commits
Repo: github.com/hasankaantan/socialpykit
