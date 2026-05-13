from fastapi.routing import APIRouter

from app.api.v1.routers import auth, dummy, monitoring, users

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
