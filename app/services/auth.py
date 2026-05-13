"""Authentication service: registration, login, and subject resolution."""

from app.core.exceptions import AlreadyExistsError, AuthenticationError
from app.core.security import (
    create_access_token,
    decode_access_token_subject,
    hash_password,
    verify_password,
)
from app.db.models.user import User
from app.repositories.user import UserRepository


class AuthService:
    """Orchestrates user-facing auth flows on top of ``UserRepository``."""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def register(self, *, email: str, password: str) -> User:
        """Create a new user with a bcrypt-hashed password.

        Raises :class:`AlreadyExistsError` if a user with ``email`` is
        already on file.
        """
        if await self._repository.get_by_email(email) is not None:
            message = "A user with this email already exists"
            raise AlreadyExistsError(message, context={"email": email})

        new_user = User(
            email=email,
            hashed_password=hash_password(password),
            is_active=True,
        )
        return await self._repository.create(new_user)

    async def authenticate(self, *, email: str, password: str) -> User:
        """Verify credentials and return the user behind them.

        Raises :class:`AuthenticationError` for missing users, wrong
        passwords, and disabled accounts. The error message is intentionally
        identical for the first two cases so the caller cannot enumerate
        valid emails.
        """
        user = await self._repository.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            message = "Invalid email or password"
            raise AuthenticationError(message)
        if not user.is_active:
            message = "User account is disabled"
            raise AuthenticationError(message)
        return user

    def create_token_for_user(self, user: User) -> str:
        """Mint a fresh access token carrying ``user.id`` as the subject."""
        return create_access_token(subject=str(user.id))

    async def resolve_user_from_token(self, token: str) -> User:
        """Decode ``token`` and return the user it represents.

        Used by the FastAPI dependency that protects authenticated routes.
        Raises :class:`AuthenticationError` for invalid tokens, unknown
        users, and disabled accounts.
        """
        subject = decode_access_token_subject(token)
        try:
            user_id = int(subject)
        except ValueError as exc:
            message = "Token subject is not a valid user id"
            raise AuthenticationError(message) from exc

        user = await self._repository.get(user_id)
        if user is None:
            message = "Token references an unknown user"
            raise AuthenticationError(message)
        if not user.is_active:
            message = "User account is disabled"
            raise AuthenticationError(message)
        return user
