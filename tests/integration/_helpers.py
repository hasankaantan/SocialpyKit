"""Shared helpers for integration tests."""

import uuid

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import UserRole
from app.repositories.user import UserRepository


async def register_and_login(
    *,
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    role: UserRole = UserRole.USER,
    email: str | None = None,
    password: str = "secret-password-123",
) -> tuple[str, str]:
    """Register a fresh user, optionally promote to admin, return (email, token).

    Promotion is done via direct repository update on the shared test
    transaction so the change is visible without committing.
    """
    actual_email = email or f"{uuid.uuid4().hex}@example.com"

    register_url = fastapi_app.url_path_for("register")
    register_response = await client.post(
        register_url,
        json={"email": actual_email, "password": password},
    )
    assert register_response.status_code == 201, register_response.text

    if role is UserRole.ADMIN:
        repo = UserRepository(dbsession)
        user = await repo.get_by_email(actual_email)
        assert user is not None
        user.role = UserRole.ADMIN
        await repo.update(user)

    login_url = fastapi_app.url_path_for("login")
    login_response = await client.post(
        login_url,
        data={"username": actual_email, "password": password},
    )
    assert login_response.status_code == 200, login_response.text
    token: str = login_response.json()["access_token"]
    return actual_email, token


def auth_header(token: str) -> dict[str, str]:
    """Build an Authorization header for ``token``."""
    return {"Authorization": f"Bearer {token}"}
