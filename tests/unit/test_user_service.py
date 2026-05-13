"""Unit tests for :class:`app.services.user.UserService`."""

from collections.abc import Sequence

import pytest
from whenever import Instant

from app.core.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)
from app.core.security import hash_password
from app.db.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.services.user import UserService


class FakeUserRepository(UserRepository):
    """In-memory stand-in for :class:`UserRepository`."""

    def __init__(self) -> None:
        self._rows: list[User] = []
        self._next_id = 1

    async def get(self, entity_id: int) -> User | None:
        return next((u for u in self._rows if u.id == entity_id), None)

    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._rows if u.email == email), None)

    async def list(self) -> Sequence[User]:
        return list(self._rows)

    async def create(self, entity: User) -> User:
        entity.id = self._next_id
        self._next_id += 1
        entity.created_at = Instant.now().to_stdlib()
        entity.updated_at = entity.created_at
        self._rows.append(entity)
        return entity

    async def update(self, entity: User) -> User:
        for index, row in enumerate(self._rows):
            if row.id == entity.id:
                self._rows[index] = entity
                return entity
        return entity

    async def delete(self, entity_id: int) -> None:
        self._rows = [u for u in self._rows if u.id != entity_id]


async def _seed_user(
    repository: FakeUserRepository,
    *,
    email: str = "alice@example.com",
    password: str = "current-password",
) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password),
        is_active=True,
        role=UserRole.USER,
    )
    return await repository.create(user)


async def test_list_users_returns_every_row() -> None:
    repository = FakeUserRepository()
    await _seed_user(repository, email="a@example.com")
    await _seed_user(repository, email="b@example.com")
    service = UserService(repository)

    result = await service.list_users()

    assert {row.email for row in result} == {"a@example.com", "b@example.com"}


async def test_update_self_changes_email() -> None:
    repository = FakeUserRepository()
    user = await _seed_user(repository)
    service = UserService(repository)

    result = await service.update_self(user, email="new@example.com")

    assert result.email == "new@example.com"


async def test_update_self_changes_password_with_correct_current() -> None:
    repository = FakeUserRepository()
    user = await _seed_user(repository, password="current-password")
    service = UserService(repository)
    original_hash = user.hashed_password

    result = await service.update_self(
        user,
        new_password="new-strong-password",
        current_password="current-password",
    )

    assert result.hashed_password != original_hash


async def test_update_self_rejects_password_change_without_current_password() -> None:
    repository = FakeUserRepository()
    user = await _seed_user(repository)
    service = UserService(repository)

    with pytest.raises(ValidationError):
        await service.update_self(user, new_password="new-strong-password")


async def test_update_self_rejects_wrong_current_password() -> None:
    repository = FakeUserRepository()
    user = await _seed_user(repository, password="current-password")
    service = UserService(repository)

    with pytest.raises(AuthenticationError):
        await service.update_self(
            user,
            new_password="new-strong-password",
            current_password="wrong-password",
        )


async def test_update_self_rejects_email_already_taken() -> None:
    repository = FakeUserRepository()
    user = await _seed_user(repository, email="alice@example.com")
    await _seed_user(repository, email="taken@example.com")
    service = UserService(repository)

    with pytest.raises(AlreadyExistsError):
        await service.update_self(user, email="taken@example.com")


async def test_update_self_no_op_when_no_fields_supplied() -> None:
    """All optional fields default to None; the service must not touch
    the user when none are provided."""
    repository = FakeUserRepository()
    user = await _seed_user(repository, email="alice@example.com")
    original_email = user.email
    original_hash = user.hashed_password
    service = UserService(repository)

    result = await service.update_self(user)

    assert result.email == original_email
    assert result.hashed_password == original_hash


async def test_delete_self_removes_the_user() -> None:
    repository = FakeUserRepository()
    user = await _seed_user(repository)
    service = UserService(repository)

    await service.delete_self(user)

    assert await repository.get(user.id) is None


async def test_update_self_allows_setting_email_to_current_value() -> None:
    """Setting email to its current value is a no-op, not a conflict."""
    repository = FakeUserRepository()
    user = await _seed_user(repository, email="alice@example.com")
    service = UserService(repository)

    result = await service.update_self(user, email="alice@example.com")

    assert result.email == "alice@example.com"


# ---- admin actions ---------------------------------------------------------


async def test_update_as_admin_changes_all_fields() -> None:
    repository = FakeUserRepository()
    target = await _seed_user(repository)
    service = UserService(repository)

    result = await service.update_as_admin(
        target.id,
        email="new@example.com",
        is_active=False,
        role=UserRole.ADMIN,
    )

    assert result.email == "new@example.com"
    assert result.is_active is False
    assert result.role == UserRole.ADMIN


async def test_update_as_admin_no_op_when_no_fields_supplied() -> None:
    repository = FakeUserRepository()
    target = await _seed_user(repository, email="alice@example.com")
    service = UserService(repository)
    original_email = target.email

    result = await service.update_as_admin(target.id)

    assert result.email == original_email


async def test_update_as_admin_allows_setting_email_to_current_value() -> None:
    repository = FakeUserRepository()
    target = await _seed_user(repository, email="alice@example.com")
    service = UserService(repository)

    result = await service.update_as_admin(target.id, email="alice@example.com")

    assert result.email == "alice@example.com"


async def test_update_as_admin_raises_when_target_missing() -> None:
    service = UserService(FakeUserRepository())

    with pytest.raises(NotFoundError):
        await service.update_as_admin(9999, email="x@example.com")


async def test_update_as_admin_rejects_email_collision() -> None:
    repository = FakeUserRepository()
    target = await _seed_user(repository, email="alice@example.com")
    await _seed_user(repository, email="taken@example.com")
    service = UserService(repository)

    with pytest.raises(AlreadyExistsError):
        await service.update_as_admin(target.id, email="taken@example.com")


async def test_delete_as_admin_removes_the_target() -> None:
    repository = FakeUserRepository()
    target = await _seed_user(repository)
    service = UserService(repository)

    await service.delete_as_admin(target.id)

    assert await repository.get(target.id) is None


async def test_delete_as_admin_raises_when_target_missing() -> None:
    service = UserService(FakeUserRepository())

    with pytest.raises(NotFoundError):
        await service.delete_as_admin(9999)
