"""Unit tests for :mod:`app.schemas.auth`."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


def test_register_request_accepts_valid_payload() -> None:
    payload = RegisterRequest(email="alice@example.com", password="strong-pw")

    assert payload.email == "alice@example.com"
    assert payload.password == "strong-pw"


def test_register_request_rejects_short_password() -> None:
    with pytest.raises(PydanticValidationError):
        RegisterRequest(email="alice@example.com", password="short")


def test_register_request_rejects_oversize_password() -> None:
    with pytest.raises(PydanticValidationError):
        RegisterRequest(email="alice@example.com", password="x" * 100)


def test_register_request_rejects_invalid_email() -> None:
    with pytest.raises(PydanticValidationError):
        RegisterRequest(email="not-an-email", password="strong-pw")


def test_login_request_accepts_valid_payload() -> None:
    payload = LoginRequest(email="alice@example.com", password="any-pw-here")

    assert payload.email == "alice@example.com"


def test_token_response_defaults_to_bearer() -> None:
    response = TokenResponse(access_token="header.payload.signature")

    assert response.token_type == "bearer"
    assert response.access_token == "header.payload.signature"


def test_user_response_omits_hashed_password() -> None:
    """The response schema must not surface the password hash even if a
    caller passes it in, since the field does not exist on the model."""
    response = UserResponse(
        id=1,
        email="alice@example.com",
        is_active=True,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    assert "hashed_password" not in response.model_dump()


def test_schemas_reject_extra_fields() -> None:
    """BaseSchema sets extra='forbid' — unexpected payload keys must fail
    fast at validation time."""
    with pytest.raises(PydanticValidationError):
        RegisterRequest.model_validate(
            {
                "email": "alice@example.com",
                "password": "strong-pw",
                "unexpected": "field",
            },
        )
