"""SQLAlchemy-backed repository for the dummy demo aggregate."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.essentials import BaseRepository
from app.db.models.dummy_model import DummyModel


class DummyRepository(BaseRepository[DummyModel, int]):
    """Concrete repository for ``DummyModel`` rows."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, entity_id: int) -> DummyModel | None:
        result = await self._session.execute(
            select(DummyModel).where(DummyModel.id == entity_id),
        )
        return result.scalars().one_or_none()

    async def list(self) -> Sequence[DummyModel]:
        result = await self._session.execute(select(DummyModel))
        return result.scalars().all()

    async def list_paginated(
        self,
        *,
        limit: int,
        offset: int,
    ) -> Sequence[DummyModel]:
        """Return a slice of dummy rows for paginated reads."""
        result = await self._session.execute(
            select(DummyModel).limit(limit).offset(offset),
        )
        return result.scalars().all()

    async def find_by_name(self, name: str) -> Sequence[DummyModel]:
        """Return every dummy row whose ``name`` matches exactly."""
        result = await self._session.execute(
            select(DummyModel).where(DummyModel.name == name),
        )
        return result.scalars().all()

    async def create(self, entity: DummyModel) -> DummyModel:
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def update(self, entity: DummyModel) -> DummyModel:
        merged = await self._session.merge(entity)
        await self._session.flush()
        return merged

    async def delete(self, entity_id: int) -> None:
        instance = await self.get(entity_id)
        if instance is not None:
            await self._session.delete(instance)
            await self._session.flush()
