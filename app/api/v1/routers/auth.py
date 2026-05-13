"""HTTP entry points for the auth domain."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.api.v1.dependencies.auth import AuthServiceDep, CurrentUserDep
from app.core.server.rate_limit import limiter
from app.schemas.auth import RegisterRequest, TokenResponse, UserResponse

router = APIRouter()


@router.post("/register", status_code=201)
@limiter.limit("3/minute")  # pyright: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
async def register(
    request: Request,  # noqa: ARG001 — required by slowapi key_func
    payload: RegisterRequest,
    service: AuthServiceDep,
) -> UserResponse:
    """Create a new user account.

    Per-IP rate limit: 3 attempts / minute. Bots that try to register
    en masse hit a 429 before reaching the bcrypt hash step.
    """
    user = await service.register(
        email=payload.email,
        password=payload.password,
    )
    return UserResponse.model_validate(user)


@router.post("/login")
@limiter.limit("5/minute")  # pyright: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
async def login(
    request: Request,  # noqa: ARG001 — required by slowapi key_func
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthServiceDep,
) -> TokenResponse:
    """Exchange email and password for a bearer access token.

    Accepts the standard OAuth2 password-grant form body so the Swagger
    UI's 'Authorize' button works out of the box. ``form.username`` is
    the email address.

    Per-IP rate limit: 5 attempts / minute. Sufficient for a typo
    correction loop, hostile to credential-stuffing.
    """
    user = await service.authenticate(email=form.username, password=form.password)
    return TokenResponse(access_token=service.create_token_for_user(user))


@router.get("/me")
async def get_me(current_user: CurrentUserDep) -> UserResponse:
    """Return the user resolved from the bearer token."""
    return UserResponse.model_validate(current_user)
