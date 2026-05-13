"""Shared pytest fixtures for unit and integration tests.

Scope discipline:

- Session-scoped fixtures bring up infrastructure that is too expensive to
  rebuild per test (the postgres test database, the SQLAlchemy engine).
- Function-scoped fixtures wrap each test in a connection-level
  transaction that is rolled back at teardown, so tests stay isolated
  even though they share the engine.
- Async fixtures all run on the session event loop
  (configured via ``asyncio_default_fixture_loop_scope = "session"`` in
  ``pyproject.toml``).
"""

from collections.abc import AsyncGenerator, Callable

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.dependencies import get_db_session
from app.db.models.dummy_model import DummyModel
from app.db.utils import create_database, drop_database
from app.settings import settings
from app.web.application import get_app


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine]:  # pyright: ignore[reportUnusedFunction]
    """Build the test postgres database, yield an engine, then drop the db.

    Runs once per pytest session.
    """
    from app.db.meta import meta
    from app.db.models import load_all_models

    load_all_models()
    await create_database()

    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()


@pytest.fixture
async def dbsession(_engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    """Yield a SQLAlchemy session inside a rolled-back transaction.

    Every test gets a fresh connection and a top-level transaction; teardown
    rolls back and closes both so the schema stays clean for the next test.
    """
    connection = await _engine.connect()
    trans = await connection.begin()
    session = async_sessionmaker(connection, expire_on_commit=False)()
    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture
def fastapi_app(dbsession: AsyncSession) -> FastAPI:
    """Return a FastAPI app whose db dependency points at the test session."""
    application = get_app()
    application.dependency_overrides[get_db_session] = lambda: dbsession
    return application


@pytest.fixture
async def client(fastapi_app: FastAPI) -> AsyncGenerator[AsyncClient]:
    """Yield an httpx AsyncClient bound to the test FastAPI app via ASGI."""
    async with AsyncClient(
        transport=ASGITransport(fastapi_app),
        base_url="http://test",
        timeout=2.0,
    ) as ac:
        yield ac


@pytest.fixture
def dummy_factory() -> Callable[..., DummyModel]:
    """Return a factory that builds ``DummyModel`` instances for tests.

    Usage::

        def test_x(dummy_factory):
            row = dummy_factory(name="explicit")
            row_with_default = dummy_factory()
    """
    counter = {"value": 0}

    def _build(name: str | None = None) -> DummyModel:
        if name is None:
            counter["value"] += 1
            name = f"dummy-{counter['value']}"
        return DummyModel(name=name)

    return _build
