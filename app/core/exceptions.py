"""Custom exception hierarchy used across services and routers.

The hierarchy splits errors by responsibility so that the API layer can map
each branch to an HTTP status code without sprinkling status logic inside
services:

    SocialpyKitError
        DomainError                 -> 4xx, caller-fixable input or state
            NotFoundError           -> 404
            AlreadyExistsError      -> 409
            ConflictError           -> 409 (general state conflict)
            ValidationError         -> 422 (semantic validation past pydantic)
        AuthenticationError         -> 401
        AuthorizationError          -> 403
        InfrastructureError         -> 5xx, dependencies and runtime issues
"""

from typing import Any


class SocialpyKitError(Exception):
    """Root exception for every error raised inside this codebase."""

    def __init__(
        self,
        message: str,
        *,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.context: dict[str, Any] = context or {}


class DomainError(SocialpyKitError):
    """Business rule violation surfaced from the services or model layer."""


class NotFoundError(DomainError):
    """Raised when a requested entity does not exist."""


class AlreadyExistsError(DomainError):
    """Raised when a uniqueness constraint would be violated."""


class ConflictError(DomainError):
    """Raised when an entity is in a state incompatible with the action."""


class ValidationError(DomainError):
    """Raised when domain-level validation rejects otherwise well-formed input.

    Pydantic handles structural validation at the API boundary. This class is
    for semantic checks that depend on domain state, for example "balance
    cannot drop below zero".
    """


class AuthenticationError(SocialpyKitError):
    """Raised when caller identity cannot be established."""


class AuthorizationError(SocialpyKitError):
    """Raised when the caller is identified but not permitted."""


class InfrastructureError(SocialpyKitError):
    """Raised for failures in a dependency the service does not own.

    Examples: database unavailable, external API timeout, broken cache.
    """
