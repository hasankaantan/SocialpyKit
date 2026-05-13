"""Business-logic service for user-management use cases.

Authentication-specific flows (register, login, token resolution) live
in :mod:`app.services.auth`. This module covers everything an
authenticated caller can do *about users*: read, update, delete.
"""

from collections.abc import Sequence

from app.db.models.user import User
from app.repositories.user import UserRepository


class UserService:
    """Orchestrates user-management use cases on top of ``UserRepository``."""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def list_users(self) -> Sequence[User]:
        """Return every user. Caller is expected to gate this on admin role."""
        return await self._repository.list()
