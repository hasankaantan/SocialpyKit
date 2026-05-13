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


async def test_update_me_changes_email(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    _, token = await register_and_login(
        fastapi_app=fastapi_app,
        client=client,
        dbsession=dbsession,
    )
    url = fastapi_app.url_path_for("update_me")

    response = await client.patch(
        url,
        headers=auth_header(token),
        json={"email": "updated@example.com"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "updated@example.com"


async def test_update_me_changes_password_and_invalidates_old_one(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    email, token = await register_and_login(
        fastapi_app=fastapi_app,
        client=client,
        dbsession=dbsession,
        password="old-password-123",
    )
    update_url = fastapi_app.url_path_for("update_me")
    login_url = fastapi_app.url_path_for("login")

    response = await client.patch(
        update_url,
        headers=auth_header(token),
        json={
            "new_password": "new-password-456",
            "current_password": "old-password-123",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    # The old password no longer works
    old_pw_login = await client.post(
        login_url,
        data={"username": email, "password": "old-password-123"},
    )
    assert old_pw_login.status_code == status.HTTP_401_UNAUTHORIZED

    # The new password does
    new_pw_login = await client.post(
        login_url,
        data={"username": email, "password": "new-password-456"},
    )
    assert new_pw_login.status_code == status.HTTP_200_OK


async def test_update_me_rejects_password_change_without_current(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    _, token = await register_and_login(
        fastapi_app=fastapi_app,
        client=client,
        dbsession=dbsession,
    )
    url = fastapi_app.url_path_for("update_me")

    response = await client.patch(
        url,
        headers=auth_header(token),
        json={"new_password": "new-strong-pw"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_update_me_rejects_wrong_current_password(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    _, token = await register_and_login(
        fastapi_app=fastapi_app,
        client=client,
        dbsession=dbsession,
    )
    url = fastapi_app.url_path_for("update_me")

    response = await client.patch(
        url,
        headers=auth_header(token),
        json={
            "new_password": "new-strong-pw",
            "current_password": "wrong-current-pw",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_delete_me_removes_the_account(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    email, token = await register_and_login(
        fastapi_app=fastapi_app,
        client=client,
        dbsession=dbsession,
    )
    delete_url = fastapi_app.url_path_for("delete_me")
    login_url = fastapi_app.url_path_for("login")
    me_url = fastapi_app.url_path_for("get_me")

    response = await client.delete(delete_url, headers=auth_header(token))
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # The token references a user that no longer exists
    me_response = await client.get(me_url, headers=auth_header(token))
    assert me_response.status_code == status.HTTP_401_UNAUTHORIZED

    # And the password no longer logs in (user is gone)
    login_response = await client.post(
        login_url,
        data={"username": email, "password": "secret-password-123"},
    )
    assert login_response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_update_me_rejects_duplicate_email(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    first_email, _ = await register_and_login(
        fastapi_app=fastapi_app,
        client=client,
        dbsession=dbsession,
    )
    _, second_token = await register_and_login(
        fastapi_app=fastapi_app,
        client=client,
        dbsession=dbsession,
    )
    url = fastapi_app.url_path_for("update_me")

    response = await client.patch(
        url,
        headers=auth_header(second_token),
        json={"email": first_email},
    )

    assert response.status_code == status.HTTP_409_CONFLICT
