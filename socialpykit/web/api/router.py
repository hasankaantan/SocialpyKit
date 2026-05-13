from fastapi.routing import APIRouter

from socialpykit.web.api import dummy, monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
