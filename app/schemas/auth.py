"""Auth-related request and response DTOs."""

from datetime import datetime
from typing import Final

from pydantic import EmailStr, Field

from app.core.essentials import BaseSchema

# Bcrypt cannot hash inputs longer than 72 bytes (see app.core.security).
# Reject oversize passwords at the api boundary rather than letting them
# reach the service and raise ValidationError mid-flight.
_PASSWORD_MIN_LENGTH: Final = 8
_PASSWORD_MAX_LENGTH: Final = 72


class RegisterRequest(BaseSchema):
    """Payload for ``POST /api/auth/register``."""

    email: EmailStr
    password: str = Field(
        min_length=_PASSWORD_MIN_LENGTH,
        max_length=_PASSWORD_MAX_LENGTH,
    )


class LoginRequest(BaseSchema):
    """Json payload for the password-grant login flow.

    The OAuth2PasswordBearer-backed endpoint accepts the standard form
    body too; this DTO documents the JSON shape that downstream clients
    (the Vue ui, a Postman collection, etc.) consume.
    """

    email: EmailStr
    password: str = Field(
        min_length=_PASSWORD_MIN_LENGTH,
        max_length=_PASSWORD_MAX_LENGTH,
    )


class TokenResponse(BaseSchema):
    """OAuth2-compatible bearer-token response."""

    access_token: str
    token_type: str = "bearer"  # noqa: S105 — oauth2 standard scheme name, not a credential


class UserResponse(BaseSchema):
    """Public projection of a ``User`` row.

    Never includes ``hashed_password`` — that field exists only inside
    the persistence layer and the auth service.
    """

    id: int
    email: EmailStr
    is_active: bool
    role: str
    created_at: datetime


class UserUpdateRequest(BaseSchema):
    """Payload for ``PATCH /api/users/me``.

    All fields are optional; supply only the ones to change. When
    ``new_password`` is provided, ``current_password`` is required so a
    stolen token alone cannot rotate the password.
    """

    email: EmailStr | None = None
    new_password: str | None = Field(
        default=None,
        min_length=_PASSWORD_MIN_LENGTH,
        max_length=_PASSWORD_MAX_LENGTH,
    )
    current_password: str | None = None
