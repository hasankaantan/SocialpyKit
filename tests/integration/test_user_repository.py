"""Integration tests for :class:`app.repositories.user.UserRepository`."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.repositories.user import UserRepository


def _build_user(email: str | None = None) -> User:
    return User(
        email=email or f"{uuid.uuid4().hex}@example.com",
        hashed_password="$2b$12$placeholder.hash.value.for.testing.purposes.only.x",  # noqa: S106 — opaque test fixture, not a real credential
    )


async def test_get_returns_existing_user(dbsession: AsyncSession) -> None:
    repository = UserRepository(dbsession)
    persisted = await repository.create(_build_user())

    fetched = await repository.get(persisted.id)

    assert fetched is not None
    assert fetched.id == persisted.id


async def test_get_returns_none_for_missing_user(dbsession: AsyncSession) -> None:
    repository = UserRepository(dbsession)

    assert await repository.get(99_999) is None


async def test_get_by_email_returns_existing_user(dbsession: AsyncSession) -> None:
    repository = UserRepository(dbsession)
    target_email = f"{uuid.uuid4().hex}@example.com"
    await repository.create(_build_user(email=target_email))

    fetched = await repository.get_by_email(target_email)

    assert fetched is not None
    assert fetched.email == target_email


async def test_get_by_email_returns_none_when_missing(dbsession: AsyncSession) -> None:
    repository = UserRepository(dbsession)

    assert await repository.get_by_email("nobody@example.com") is None


async def test_list_returns_every_user(dbsession: AsyncSession) -> None:
    repository = UserRepository(dbsession)
    emails = {f"{uuid.uuid4().hex}@example.com" for _ in range(3)}
    for email in emails:
        await repository.create(_build_user(email=email))

    rows = await repository.list()

    assert {row.email for row in rows} == emails


async def test_update_persists_changes(dbsession: AsyncSession) -> None:
    repository = UserRepository(dbsession)
    persisted = await repository.create(_build_user())
    persisted.is_active = False

    await repository.update(persisted)

    refetched = await repository.get(persisted.id)
    assert refetched is not None
    assert refetched.is_active is False


async def test_delete_removes_user(dbsession: AsyncSession) -> None:
    repository = UserRepository(dbsession)
    persisted = await repository.create(_build_user())

    await repository.delete(persisted.id)

    assert await repository.get(persisted.id) is None


async def test_delete_is_noop_for_missing_id(dbsession: AsyncSession) -> None:
    repository = UserRepository(dbsession)

    await repository.delete(99_999)

    assert await repository.list() == []
