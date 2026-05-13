"""Unit tests for :class:`app.services.auth.AuthService`."""

from collections.abc import Sequence

import pytest
from whenever import Instant

from app.core.exceptions import AlreadyExistsError, AuthenticationError
from app.db.models.user import User
from app.repositories.user import UserRepository
from app.services.auth import AuthService


class FakeUserRepository(UserRepository):
    """In-memory stand-in for :class:`UserRepository`.

    Mirrors the FakeDummyRepository pattern: inherit from the real class
    so the service constructor accepts it without type narrowing, then
    skip ``__init__`` to avoid needing a real sqlalchemy session.
    """

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


# ---- register --------------------------------------------------------------


async def test_register_creates_new_user() -> None:
    service = AuthService(FakeUserRepository())

    user = await service.register(email="alice@example.com", password="strong-pw")

    assert user.id == 1
    assert user.email == "alice@example.com"


async def test_register_hashes_the_password() -> None:
    service = AuthService(FakeUserRepository())

    user = await service.register(email="alice@example.com", password="strong-pw")

    assert user.hashed_password != "strong-pw"
    assert user.hashed_password.startswith("$2b$")


async def test_register_raises_when_email_already_exists() -> None:
    repository = FakeUserRepository()
    service = AuthService(repository)
    await service.register(email="alice@example.com", password="strong-pw")

    with pytest.raises(AlreadyExistsError):
        await service.register(email="alice@example.com", password="other-pw")


# ---- authenticate ----------------------------------------------------------


async def test_authenticate_returns_user_for_correct_credentials() -> None:
    repository = FakeUserRepository()
    service = AuthService(repository)
    created = await service.register(
        email="alice@example.com",
        password="strong-pw",
    )

    fetched = await service.authenticate(
        email="alice@example.com",
        password="strong-pw",
    )

    assert fetched.id == created.id


async def test_authenticate_raises_for_unknown_email() -> None:
    service = AuthService(FakeUserRepository())

    with pytest.raises(AuthenticationError):
        await service.authenticate(email="ghost@example.com", password="any-pw")


async def test_authenticate_raises_for_wrong_password() -> None:
    repository = FakeUserRepository()
    service = AuthService(repository)
    await service.register(email="alice@example.com", password="strong-pw")

    with pytest.raises(AuthenticationError):
        await service.authenticate(
            email="alice@example.com",
            password="wrong-password",
        )


async def test_authenticate_raises_for_inactive_user() -> None:
    repository = FakeUserRepository()
    service = AuthService(repository)
    user = await service.register(email="alice@example.com", password="strong-pw")
    user.is_active = False

    with pytest.raises(AuthenticationError):
        await service.authenticate(
            email="alice@example.com",
            password="strong-pw",
        )


# ---- tokens ----------------------------------------------------------------


async def test_create_token_for_user_returns_a_string() -> None:
    service = AuthService(FakeUserRepository())
    user = await service.register(email="alice@example.com", password="strong-pw")

    token = service.create_token_for_user(user)

    assert isinstance(token, str)
    assert token.count(".") == 2  # header.payload.signature


async def test_resolve_user_from_token_round_trip() -> None:
    repository = FakeUserRepository()
    service = AuthService(repository)
    user = await service.register(email="alice@example.com", password="strong-pw")
    token = service.create_token_for_user(user)

    resolved = await service.resolve_user_from_token(token)

    assert resolved.id == user.id


async def test_resolve_user_from_token_raises_for_non_integer_subject() -> None:
    """Tokens minted by external systems may carry a non-integer sub. The
    service rejects them rather than crashing inside int()."""
    from app.core.security import create_access_token

    token = create_access_token(subject="not-a-user-id")
    service = AuthService(FakeUserRepository())

    with pytest.raises(AuthenticationError):
        await service.resolve_user_from_token(token)


async def test_resolve_user_from_token_raises_for_unknown_user() -> None:
    """Token decodes cleanly but the user id no longer exists."""
    from app.core.security import create_access_token

    token = create_access_token(subject="9999")
    service = AuthService(FakeUserRepository())

    with pytest.raises(AuthenticationError):
        await service.resolve_user_from_token(token)


async def test_resolve_user_from_token_raises_for_inactive_user() -> None:
    repository = FakeUserRepository()
    service = AuthService(repository)
    user = await service.register(email="alice@example.com", password="strong-pw")
    token = service.create_token_for_user(user)
    user.is_active = False

    with pytest.raises(AuthenticationError):
        await service.resolve_user_from_token(token)
