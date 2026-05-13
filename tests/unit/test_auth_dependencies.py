"""Unit tests for :mod:`app.api.v1.dependencies.auth`."""

import pytest

from app.api.v1.dependencies.auth import get_admin_user
from app.core.exceptions import AuthorizationError
from app.db.models.user import User, UserRole


def _make_user(*, role: UserRole) -> User:
    user = User(
        email="caller@example.com",
        hashed_password="x",
        is_active=True,
        role=role,
    )
    user.id = 1
    return user


async def test_get_admin_user_returns_user_when_role_is_admin() -> None:
    admin = _make_user(role=UserRole.ADMIN)

    result = await get_admin_user(admin)

    assert result is admin


async def test_get_admin_user_raises_when_role_is_user() -> None:
    regular = _make_user(role=UserRole.USER)

    with pytest.raises(AuthorizationError) as exc_info:
        await get_admin_user(regular)

    assert exc_info.value.context == {"user_id": 1}
