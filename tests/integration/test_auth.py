"""Integration tests for the auth endpoints.

These exercise the full stack: FastAPI routing, OAuth2 dependency
resolution, the service and repository layers, the real test database,
and the domain-exception → HTTP-status handlers.
"""

import uuid

from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status


def _unique_email() -> str:
    return f"{uuid.uuid4().hex}@example.com"


# ---- register --------------------------------------------------------------


async def test_register_creates_user_and_returns_dto(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    url = fastapi_app.url_path_for("register")
    email = _unique_email()

    response = await client.post(
        url,
        json={"email": email, "password": "strong-password"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["email"] == email
    assert body["is_active"] is True
    assert "hashed_password" not in body


async def test_register_rejects_duplicate_email(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    url = fastapi_app.url_path_for("register")
    email = _unique_email()

    first = await client.post(
        url,
        json={"email": email, "password": "strong-password"},
    )
    assert first.status_code == status.HTTP_201_CREATED

    second = await client.post(
        url,
        json={"email": email, "password": "another-password"},
    )

    assert second.status_code == status.HTTP_409_CONFLICT


async def test_register_rejects_invalid_payload(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    url = fastapi_app.url_path_for("register")

    response = await client.post(
        url,
        json={"email": "not-an-email", "password": "short"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---- login -----------------------------------------------------------------


async def test_login_returns_bearer_token_for_correct_credentials(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    register_url = fastapi_app.url_path_for("register")
    login_url = fastapi_app.url_path_for("login")
    email = _unique_email()

    await client.post(
        register_url,
        json={"email": email, "password": "strong-password"},
    )

    response = await client.post(
        login_url,
        data={"username": email, "password": "strong-password"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"].count(".") == 2


async def test_login_rejects_unknown_email(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    login_url = fastapi_app.url_path_for("login")

    response = await client.post(
        login_url,
        data={"username": "ghost@example.com", "password": "anything"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_login_rejects_wrong_password(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    register_url = fastapi_app.url_path_for("register")
    login_url = fastapi_app.url_path_for("login")
    email = _unique_email()

    await client.post(
        register_url,
        json={"email": email, "password": "strong-password"},
    )

    response = await client.post(
        login_url,
        data={"username": email, "password": "wrong-password"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---- me --------------------------------------------------------------------


async def test_get_me_returns_current_user_for_valid_token(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    register_url = fastapi_app.url_path_for("register")
    login_url = fastapi_app.url_path_for("login")
    me_url = fastapi_app.url_path_for("get_me")
    email = _unique_email()

    await client.post(
        register_url,
        json={"email": email, "password": "strong-password"},
    )
    login = await client.post(
        login_url,
        data={"username": email, "password": "strong-password"},
    )
    token = login.json()["access_token"]

    response = await client.get(
        me_url,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["email"] == email


async def test_get_me_rejects_missing_token(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    me_url = fastapi_app.url_path_for("get_me")

    response = await client.get(me_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_me_rejects_invalid_token(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    me_url = fastapi_app.url_path_for("get_me")

    response = await client.get(
        me_url,
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
