"""Business-logic service for user-management use cases.

Authentication-specific flows (register, login, token resolution) live
in :mod:`app.services.auth`. This module covers everything an
authenticated caller can do *about users*: read, update, delete.
"""

from collections.abc import Sequence

from app.core.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)
from app.core.security import hash_password, verify_password
from app.db.models.user import User, UserRole
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

    async def delete_self(self, user: User) -> None:
        """Delete the caller's own user row."""
        await self._repository.delete(user.id)

    async def update_as_admin(
        self,
        user_id: int,
        *,
        email: str | None = None,
        is_active: bool | None = None,
        role: UserRole | None = None,
    ) -> User:
        """Apply an admin-controlled partial update to ``user_id``.

        Raises :class:`NotFoundError` if the target does not exist and
        :class:`AlreadyExistsError` if the new email collides with
        another user.
        """
        target = await self._repository.get(user_id)
        if target is None:
            message = f"User {user_id} not found"
            raise NotFoundError(message, context={"user_id": user_id})

        if email is not None and email != target.email:
            existing = await self._repository.get_by_email(email)
            if existing is not None and existing.id != target.id:
                message = "A user with this email already exists"
                raise AlreadyExistsError(message, context={"email": email})
            target.email = email

        if is_active is not None:
            target.is_active = is_active

        if role is not None:
            target.role = role

        return await self._repository.update(target)

    async def delete_as_admin(self, user_id: int) -> None:
        """Delete ``user_id``; raises :class:`NotFoundError` if missing."""
        target = await self._repository.get(user_id)
        if target is None:
            message = f"User {user_id} not found"
            raise NotFoundError(message, context={"user_id": user_id})
        await self._repository.delete(user_id)
