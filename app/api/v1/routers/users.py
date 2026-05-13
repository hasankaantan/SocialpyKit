"""HTTP entry points for the user-management domain."""

from fastapi import APIRouter

from app.api.v1.dependencies.auth import AdminUserDep
from app.api.v1.dependencies.user import UserServiceDep
from app.schemas.auth import UserResponse

router = APIRouter()


@router.get("/")
async def list_users(
    _admin: AdminUserDep,
    service: UserServiceDep,
) -> list[UserResponse]:
    """Return every user. Admin-only; non-admin callers get HTTP 403."""
    users = await service.list_users()
    return [UserResponse.model_validate(user) for user in users]
