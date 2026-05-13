"""HTTP entry points for the auth domain."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import RegisterRequest, TokenResponse, UserResponse
from app.web.api.auth.dependencies import AuthServiceDep, CurrentUserDep

router = APIRouter()


@router.post("/register", status_code=201)
async def register(
    payload: RegisterRequest,
    service: AuthServiceDep,
) -> UserResponse:
    """Create a new user account."""
    user = await service.register(
        email=payload.email,
        password=payload.password,
    )
    return UserResponse.model_validate(user)


@router.post("/login")
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthServiceDep,
) -> TokenResponse:
    """Exchange email and password for a bearer access token.

    Accepts the standard OAuth2 password-grant form body so the Swagger
    UI's 'Authorize' button works out of the box. ``form.username`` is
    the email address.
    """
    user = await service.authenticate(email=form.username, password=form.password)
    return TokenResponse(access_token=service.create_token_for_user(user))


@router.get("/me")
async def get_me(current_user: CurrentUserDep) -> UserResponse:
    """Return the user resolved from the bearer token."""
    return UserResponse.model_validate(current_user)
