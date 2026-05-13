"""Business-logic service for the dummy demo aggregate."""

from collections.abc import Sequence

from app.core.exceptions import NotFoundError
from app.db.models.dummy_model import DummyModel
from app.repositories.dummy import DummyRepository


class DummyService:
    """Orchestrates dummy-aggregate use cases on top of ``DummyRepository``."""

    def __init__(self, repository: DummyRepository) -> None:
        self._repository = repository

    async def list_dummies(
        self,
        *,
        limit: int,
        offset: int,
    ) -> Sequence[DummyModel]:
        """Return a paginated slice of dummy rows."""
        return await self._repository.list_paginated(limit=limit, offset=offset)

    async def create_dummy(self, name: str) -> DummyModel:
        """Persist a new dummy with the given ``name``."""
        return await self._repository.create(DummyModel(name=name))

    async def get_dummy(self, entity_id: int) -> DummyModel:
        """Return the dummy with ``entity_id`` or raise ``NotFoundError``."""
        instance = await self._repository.get(entity_id)
        if instance is None:
            message = f"Dummy {entity_id} not found"
            raise NotFoundError(message, context={"entity_id": entity_id})
        return instance
