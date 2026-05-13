"""Integration tests for the user-management endpoints."""

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.models.user import UserRole
from tests.integration._helpers import auth_header, register_and_login


async def test_list_users_returns_every_user_for_admin(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    admin_email, admin_token = await register_and_login(
        fastapi_app=fastapi_app,
        client=client,
        dbsession=dbsession,
        role=UserRole.ADMIN,
    )
    user_email, _ = await register_and_login(
        fastapi_app=fastapi_app,
        client=client,
        dbsession=dbsession,
        role=UserRole.USER,
    )

    url = fastapi_app.url_path_for("list_users")
    response = await client.get(url, headers=auth_header(admin_token))

    assert response.status_code == status.HTTP_200_OK
    emails = {row["email"] for row in response.json()}
    assert {admin_email, user_email} <= emails


async def test_list_users_rejects_non_admin_with_403(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    _, token = await register_and_login(
        fastapi_app=fastapi_app,
        client=client,
        dbsession=dbsession,
        role=UserRole.USER,
    )

    url = fastapi_app.url_path_for("list_users")
    response = await client.get(url, headers=auth_header(token))

    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_list_users_rejects_unauthenticated_with_401(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    url = fastapi_app.url_path_for("list_users")
    response = await client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
