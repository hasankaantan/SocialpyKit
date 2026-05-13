"""Integration tests for :class:`app.repositories.dummy.DummyRepository`.

Exercises every public method against the real test database so the
SQLAlchemy queries are covered end to end.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.dummy_model import DummyModel
from app.repositories.dummy import DummyRepository


async def test_get_returns_existing_row(dbsession: AsyncSession) -> None:
    repository = DummyRepository(dbsession)
    persisted = await repository.create(DummyModel(name=uuid.uuid4().hex))

    fetched = await repository.get(persisted.id)

    assert fetched is not None
    assert fetched.id == persisted.id


async def test_get_returns_none_for_missing_id(dbsession: AsyncSession) -> None:
    repository = DummyRepository(dbsession)

    assert await repository.get(99_999) is None


async def test_list_returns_every_row(dbsession: AsyncSession) -> None:
    repository = DummyRepository(dbsession)
    names = [uuid.uuid4().hex for _ in range(3)]
    for name in names:
        await repository.create(DummyModel(name=name))

    rows = await repository.list()

    assert {row.name for row in rows} == set(names)


async def test_list_paginated_slices_results(dbsession: AsyncSession) -> None:
    repository = DummyRepository(dbsession)
    for index in range(4):
        await repository.create(DummyModel(name=f"row-{index}"))

    page = await repository.list_paginated(limit=2, offset=1)

    assert [row.name for row in page] == ["row-1", "row-2"]


async def test_find_by_name_matches_exact(dbsession: AsyncSession) -> None:
    repository = DummyRepository(dbsession)
    target = uuid.uuid4().hex
    await repository.create(DummyModel(name=target))
    await repository.create(DummyModel(name=uuid.uuid4().hex))

    matches = await repository.find_by_name(target)

    assert len(matches) == 1
    assert matches[0].name == target


async def test_update_persists_changes(dbsession: AsyncSession) -> None:
    repository = DummyRepository(dbsession)
    persisted = await repository.create(DummyModel(name="before"))
    persisted.name = "after"

    updated = await repository.update(persisted)

    refetched = await repository.get(updated.id)
    assert refetched is not None
    assert refetched.name == "after"


async def test_delete_removes_row(dbsession: AsyncSession) -> None:
    repository = DummyRepository(dbsession)
    persisted = await repository.create(DummyModel(name="to-be-deleted"))

    await repository.delete(persisted.id)

    assert await repository.get(persisted.id) is None


async def test_delete_is_noop_for_missing_id(dbsession: AsyncSession) -> None:
    repository = DummyRepository(dbsession)

    await repository.delete(99_999)

    assert await repository.list() == []
