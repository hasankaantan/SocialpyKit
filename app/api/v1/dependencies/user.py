"""FastAPI dependencies for the user-management domain."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.db import get_db_session
from app.repositories.user import UserRepository
from app.services.user import UserService


def get_user_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserService:
    """Compose :class:`UserService` for dependency injection."""
    return UserService(UserRepository(session))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
