"""Unit tests for :mod:`app.core.security`."""

from datetime import timedelta

import pytest

from app.core.exceptions import AuthenticationError, ValidationError
from app.core.security import (
    create_access_token,
    decode_access_token_subject,
    hash_password,
    verify_password,
)

# ---- password hashing ------------------------------------------------------


def test_hash_password_returns_different_hash_per_call() -> None:
    """Each bcrypt hash includes a fresh salt, so two hashes of the same
    plaintext should never collide."""
    first = hash_password("secret-pw")
    second = hash_password("secret-pw")

    assert first != second
    assert first != "secret-pw"


def test_verify_password_returns_true_for_matching_hash() -> None:
    hashed = hash_password("correct-horse-battery-staple")

    assert verify_password("correct-horse-battery-staple", hashed) is True


def test_verify_password_returns_false_for_wrong_password() -> None:
    hashed = hash_password("the-right-one")

    assert verify_password("the-wrong-one", hashed) is False


def test_hash_password_rejects_oversize_input() -> None:
    """Bcrypt cannot hash more than 72 bytes; the helper must surface this
    as a domain validation error rather than silently truncating."""
    too_long = "x" * 100

    with pytest.raises(ValidationError):
        hash_password(too_long)


def test_verify_password_returns_false_for_oversize_input() -> None:
    """Long passwords are simply rejected at verify time so the caller
    treats the result as a single boolean."""
    hashed = hash_password("ok-length")

    assert verify_password("x" * 100, hashed) is False


def test_verify_password_returns_false_for_malformed_hash() -> None:
    """Garbage hashes raise ValueError inside bcrypt; the helper catches
    that and returns False so callers can stay branch-free."""
    assert verify_password("any-password", "not-a-real-bcrypt-hash") is False


# ---- access tokens ---------------------------------------------------------


def test_create_access_token_round_trip() -> None:
    """A freshly minted token decodes to the original subject."""
    token = create_access_token("user-123")

    assert decode_access_token_subject(token) == "user-123"


def test_create_access_token_respects_explicit_expires_delta() -> None:
    """A non-default expires_delta still produces a valid token (we only
    check that the round-trip works; the in-token expiry value is opaque)."""
    token = create_access_token("user-123", expires_delta=timedelta(seconds=60))

    assert decode_access_token_subject(token) == "user-123"


def test_decode_access_token_raises_on_expired_token() -> None:
    """A token whose exp is in the past raises AuthenticationError."""
    token = create_access_token("user-123", expires_delta=timedelta(seconds=-1))

    with pytest.raises(AuthenticationError):
        decode_access_token_subject(token)


def test_decode_access_token_raises_on_tampered_token() -> None:
    """Mutating any byte of a signed jwt invalidates the signature."""
    token = create_access_token("user-123")
    tampered = token[:-2] + ("xx" if not token.endswith("xx") else "yy")

    with pytest.raises(AuthenticationError):
        decode_access_token_subject(tampered)


def test_decode_access_token_raises_on_garbage_input() -> None:
    with pytest.raises(AuthenticationError):
        decode_access_token_subject("not-a-jwt")


def test_decode_access_token_raises_when_subject_claim_missing() -> None:
    """Tokens minted with an empty subject are rejected at decode time."""
    import jwt

    from app.settings import settings

    payload = {"sub": "", "iat": 0, "exp": 9_999_999_999}
    token = jwt.encode(  # pyright: ignore[reportUnknownMemberType]
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(AuthenticationError):
        decode_access_token_subject(token)
