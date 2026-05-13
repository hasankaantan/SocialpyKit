"""FastAPI dependencies for the auth domain."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.db import get_db_session
from app.core.exceptions import AuthorizationError
from app.db.models.user import User, UserRole
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


async def get_admin_user(current_user: CurrentUserDep) -> User:
    """Allow the request through only if the resolved user is an admin.

    Raises :class:`AuthorizationError` (mapped to HTTP 403 by the global
    handler) when the user lacks the admin role.
    """
    if current_user.role is not UserRole.ADMIN:
        message = "Admin role required for this action"
        raise AuthorizationError(message, context={"user_id": current_user.id})
    return current_user


AdminUserDep = Annotated[User, Depends(get_admin_user)]
