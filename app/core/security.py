"""Security primitives: password hashing and JWT encode / decode.

The functions in this module are pure — they take strings, return strings,
and raise typed exceptions on failure. Higher-level orchestration (looking
up the user behind a subject, mapping to HTTP responses) lives in
``app.services.auth`` and the auth router.
"""

from datetime import timedelta
from typing import Any, Final

import bcrypt
import jwt
from whenever import Instant

from app.core.exceptions import AuthenticationError, ValidationError
from app.settings import settings

# bcrypt cannot hash inputs longer than 72 bytes. Rather than silently
# truncating (which would let two distinct long passwords map to the same
# hash), reject the input at the boundary.
_BCRYPT_MAX_PASSWORD_BYTES: Final = 72


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash for ``plain_password``.

    Raises :class:`ValidationError` if the utf-8 encoding exceeds bcrypt's
    72-byte limit.
    """
    encoded = plain_password.encode("utf-8")
    if len(encoded) > _BCRYPT_MAX_PASSWORD_BYTES:
        message = (
            f"Password is too long for bcrypt "
            f"({len(encoded)} bytes > {_BCRYPT_MAX_PASSWORD_BYTES} bytes)"
        )
        raise ValidationError(message)
    return bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if ``plain_password`` matches ``hashed_password``.

    Returns False (rather than raising) for malformed hashes and for inputs
    that exceed bcrypt's 72-byte limit, so callers can treat the result as
    a single boolean.
    """
    encoded = plain_password.encode("utf-8")
    if len(encoded) > _BCRYPT_MAX_PASSWORD_BYTES:
        return False
    try:
        return bcrypt.checkpw(encoded, hashed_password.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Encode a signed JWT carrying ``subject`` as the ``sub`` claim.

    ``expires_delta`` overrides the default access-token TTL from settings.
    Timestamps are produced via :mod:`whenever` so they are unambiguously
    UTC regardless of deployment timezone.
    """
    issued_at = Instant.now().to_stdlib()
    delta = expires_delta or timedelta(
        minutes=settings.jwt_access_token_expire_minutes,
    )
    expires_at = issued_at + delta
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expires_at,
        "iat": issued_at,
    }
    return jwt.encode(  # pyright: ignore[reportUnknownMemberType]
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token_subject(token: str) -> str:
    """Decode ``token`` and return its ``sub`` claim.

    Raises :class:`AuthenticationError` on any decoding, signature, or
    expiry failure, and on a malformed ``sub`` claim.
    """
    try:
        payload: dict[str, Any] = jwt.decode(  # pyright: ignore[reportUnknownMemberType]
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        message = "Invalid or expired authentication token"
        raise AuthenticationError(message) from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        message = "Authentication token is missing a valid subject claim"
        raise AuthenticationError(message)
    return subject
