"""Business-logic service for user-management use cases.

Authentication-specific flows (register, login, token resolution) live
in :mod:`app.services.auth`. This module covers everything an
authenticated caller can do *about users*: read, update, delete.
"""

from collections.abc import Sequence

from app.core.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    ValidationError,
)
from app.core.security import hash_password, verify_password
from app.db.models.user import User
from app.repositories.user import UserRepository


class UserService:
    """Orchestrates user-management use cases on top of ``UserRepository``."""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def list_users(self) -> Sequence[User]:
        """Return every user. Caller is expected to gate this on admin role."""
        return await self._repository.list()

    async def update_self(
        self,
        user: User,
        *,
        email: str | None = None,
        new_password: str | None = None,
        current_password: str | None = None,
    ) -> User:
        """Apply a partial update to ``user``.

        Rules:

        - When ``new_password`` is set, ``current_password`` must be
          provided and verify against the stored hash; otherwise a
          :class:`ValidationError` or :class:`AuthenticationError` is
          raised so the caller cannot rotate a password using a stolen
          token alone.
        - When ``email`` is set and already belongs to another user, a
          :class:`AlreadyExistsError` is raised.
        """
        if new_password is not None:
            if current_password is None:
                message = "current_password is required when changing the password"
                raise ValidationError(message)
            if not verify_password(current_password, user.hashed_password):
                message = "current_password does not match"
                raise AuthenticationError(message)
            user.hashed_password = hash_password(new_password)

        if email is not None and email != user.email:
            existing = await self._repository.get_by_email(email)
            if existing is not None and existing.id != user.id:
                message = "A user with this email already exists"
                raise AlreadyExistsError(message, context={"email": email})
            user.email = email

        return await self._repository.update(user)
