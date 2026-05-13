"""SQLAlchemy-backed repository for the user aggregate."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.essentials import BaseRepository
from app.db.models.user import User


class UserRepository(BaseRepository[User, int]):
    """Concrete repository for ``User`` rows."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, entity_id: int) -> User | None:
        result = await self._session.execute(
            select(User).where(User.id == entity_id),
        )
        return result.scalars().one_or_none()

    async def list(self) -> Sequence[User]:
        result = await self._session.execute(select(User))
        return result.scalars().all()

    async def get_by_email(self, email: str) -> User | None:
        """Return the user whose email matches exactly, or None."""
        result = await self._session.execute(
            select(User).where(User.email == email),
        )
        return result.scalars().one_or_none()

    async def create(self, entity: User) -> User:
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def update(self, entity: User) -> User:
        merged = await self._session.merge(entity)
        await self._session.flush()
        return merged

    async def delete(self, entity_id: int) -> None:
        instance = await self.get(entity_id)
        if instance is not None:
            await self._session.delete(instance)
            await self._session.flush()
