"""FastAPI dependencies for the auth domain."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.db import get_db_session
from app.db.models.user import User
from app.repositories.user import UserRepository
from app.services.auth import AuthService

# tokenUrl is documented to the OpenAPI consumers (Swagger UI's
# 'Authorize' button posts to this path). It is relative to the api prefix.
_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthService:
    """Compose :class:`AuthService` for dependency injection."""
    return AuthService(UserRepository(session))


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(
    token: Annotated[str, Depends(_oauth2_scheme)],
    service: AuthServiceDep,
) -> User:
    """Resolve the user behind the bearer token in the Authorization header."""
    return await service.resolve_user_from_token(token)


CurrentUserDep = Annotated[User, Depends(get_current_user)]
