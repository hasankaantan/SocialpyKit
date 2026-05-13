"""Unit tests for the domain exception → HTTP handlers in application.py."""

import json
from typing import cast

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AlreadyExistsError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
)
from app.web.application import (
    handle_already_exists,
    handle_authentication,
    handle_authorization,
    handle_not_found,
    handle_validation,
)

_FAKE_REQUEST = Request(scope={"type": "http", "headers": [], "method": "GET"})


def _body(response: JSONResponse) -> dict[str, str]:
    """Pull the JSON body out of a JSONResponse for assertions."""
    raw = cast("bytes", response.body)
    parsed: dict[str, str] = json.loads(raw)
    return parsed


async def test_handle_not_found_returns_404() -> None:
    response = await handle_not_found(_FAKE_REQUEST, NotFoundError("missing"))

    assert response.status_code == 404
    assert _body(response) == {"detail": "missing"}


async def test_handle_already_exists_returns_409() -> None:
    response = await handle_already_exists(
        _FAKE_REQUEST,
        AlreadyExistsError("duplicate email"),
    )

    assert response.status_code == 409
    assert _body(response) == {"detail": "duplicate email"}


async def test_handle_validation_returns_422() -> None:
    response = await handle_validation(_FAKE_REQUEST, ValidationError("bad value"))

    assert response.status_code == 422
    assert _body(response) == {"detail": "bad value"}


async def test_handle_authentication_returns_401_with_bearer_challenge() -> None:
    response = await handle_authentication(
        _FAKE_REQUEST,
        AuthenticationError("no token"),
    )

    assert response.status_code == 401
    assert _body(response) == {"detail": "no token"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


async def test_handle_authorization_returns_403() -> None:
    response = await handle_authorization(
        _FAKE_REQUEST,
        AuthorizationError("not allowed"),
    )

    assert response.status_code == 403
    assert _body(response) == {"detail": "not allowed"}
