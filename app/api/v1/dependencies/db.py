from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


async def get_db_session(  # pragma: no cover
    request: Request,
) -> AsyncGenerator[AsyncSession]:
    """Yield a SQLAlchemy session per request and commit/close on teardown.

    Tests override this dependency via ``app.dependency_overrides`` to inject
    a transaction-scoped session bound to the test database, so the body
    below only runs in production.
    """
    session: AsyncSession = request.app.state.db_session_factory()
    try:
        yield session
    finally:
        await session.commit()
        await session.close()
