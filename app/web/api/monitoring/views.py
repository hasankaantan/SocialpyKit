"""Monitoring endpoints used by load balancers, kubernetes probes, etc."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.essentials import BaseSchema
from app.db.dependencies import get_db_session

router = APIRouter()


class HealthResponse(BaseSchema):
    """Payload returned by ``GET /api/health``."""

    status: str
    database: str


@router.get("/health")
async def health_check(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    response: Response,
) -> HealthResponse:
    """Verify the application is up and postgres is reachable.

    Returns 200 with ``status='ok'`` when the database responds to a
    cheap ``SELECT 1``. Returns 503 with ``status='degraded'`` when the
    database is unreachable so load balancers and kubernetes probes can
    drain traffic from the instance.
    """
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError:  # pragma: no cover — db-down branch
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(status="degraded", database="unreachable")
    return HealthResponse(status="ok", database="ok")
