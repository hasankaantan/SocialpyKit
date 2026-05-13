"""Unit tests for :class:`app.services.dummy.DummyService`.

These tests use an in-memory fake repository so the service is exercised in
isolation from SQLAlchemy. They cover the public contract: pagination,
creation, lookup, and not-found semantics.
"""

from collections.abc import Sequence

import pytest

from app.core.exceptions import NotFoundError
from app.db.models.dummy_model import DummyModel
from app.repositories.dummy import DummyRepository
from app.services.dummy import DummyService


class FakeDummyRepository(DummyRepository):
    """In-memory stand-in for :class:`app.repositories.dummy.DummyRepository`.

    Inherits from the real class so the service can accept it without type
    narrowing, but skips the parent ``__init__`` to avoid needing a real
    SQLAlchemy session. Every method is overridden to use the in-memory
    list, so the parent's session attribute is never touched.
    """

    def __init__(self) -> None:
        self._rows: list[DummyModel] = []
        self._next_id = 1

    async def get(self, entity_id: int) -> DummyModel | None:
        return next((r for r in self._rows if r.id == entity_id), None)

    async def list(self) -> Sequence[DummyModel]:
        return list(self._rows)

    async def list_paginated(
        self,
        *,
        limit: int,
        offset: int,
    ) -> Sequence[DummyModel]:
        return self._rows[offset : offset + limit]

    async def create(self, entity: DummyModel) -> DummyModel:
        entity.id = self._next_id
        self._next_id += 1
        self._rows.append(entity)
        return entity

    async def update(self, entity: DummyModel) -> DummyModel:
        for index, row in enumerate(self._rows):
            if row.id == entity.id:
                self._rows[index] = entity
                return entity
        message = f"Dummy {entity.id} not found"
        raise NotFoundError(message)

    async def delete(self, entity_id: int) -> None:
        self._rows = [r for r in self._rows if r.id != entity_id]


async def test_create_dummy_returns_persisted_instance() -> None:
    service = DummyService(FakeDummyRepository())

    result = await service.create_dummy(name="alpha")

    assert result.name == "alpha"
    assert result.id == 1


async def test_create_dummy_assigns_incrementing_ids() -> None:
    service = DummyService(FakeDummyRepository())

    first = await service.create_dummy(name="first")
    second = await service.create_dummy(name="second")

    assert first.id == 1
    assert second.id == 2


async def test_list_dummies_returns_paginated_slice() -> None:
    service = DummyService(FakeDummyRepository())
    for name in ("a", "b", "c", "d"):
        await service.create_dummy(name=name)

    result = await service.list_dummies(limit=2, offset=1)

    assert [row.name for row in result] == ["b", "c"]


async def test_list_dummies_empty_when_repository_is_empty() -> None:
    service = DummyService(FakeDummyRepository())

    result = await service.list_dummies(limit=10, offset=0)

    assert list(result) == []


async def test_get_dummy_returns_existing_row() -> None:
    service = DummyService(FakeDummyRepository())
    created = await service.create_dummy(name="present")

    fetched = await service.get_dummy(entity_id=created.id)

    assert fetched.id == created.id
    assert fetched.name == "present"


async def test_get_dummy_raises_not_found_for_missing_id() -> None:
    service = DummyService(FakeDummyRepository())

    with pytest.raises(NotFoundError) as exc_info:
        await service.get_dummy(entity_id=999)

    assert exc_info.value.context == {"entity_id": 999}
