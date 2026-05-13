from fastapi.routing import APIRouter

from app.web.api import auth, dummy, monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
