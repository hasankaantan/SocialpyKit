"""HTTP entry points for the user-management domain."""

from fastapi import APIRouter

from app.api.v1.dependencies.auth import AdminUserDep, CurrentUserDep
from app.api.v1.dependencies.user import UserServiceDep
from app.schemas.auth import UserResponse, UserUpdateRequest

router = APIRouter()


@router.get("/")
async def list_users(
    _admin: AdminUserDep,
    service: UserServiceDep,
) -> list[UserResponse]:
    """Return every user. Admin-only; non-admin callers get HTTP 403."""
    users = await service.list_users()
    return [UserResponse.model_validate(user) for user in users]


@router.patch("/me")
async def update_me(
    payload: UserUpdateRequest,
    current_user: CurrentUserDep,
    service: UserServiceDep,
) -> UserResponse:
    """Update the caller's own profile (email and/or password)."""
    updated = await service.update_self(
        current_user,
        email=payload.email,
        new_password=payload.new_password,
        current_password=payload.current_password,
    )
    return UserResponse.model_validate(updated)
