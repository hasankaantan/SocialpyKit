"""HTTP entry points for the dummy demo aggregate.

Routers depend on services, never on repositories or models directly.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.repositories.dummy import DummyRepository
from app.services.dummy import DummyService
from app.web.api.dummy.schema import DummyModelDTO, DummyModelInputDTO

router = APIRouter()


def get_dummy_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> DummyService:
    """Compose ``DummyService`` for FastAPI dependency injection."""
    return DummyService(DummyRepository(session))


DummyServiceDep = Annotated[DummyService, Depends(get_dummy_service)]


@router.get("/")
async def get_dummy_models(
    service: DummyServiceDep,
    limit: int = 10,
    offset: int = 0,
) -> list[DummyModelDTO]:
    """Return a paginated list of dummy rows."""
    instances = await service.list_dummies(limit=limit, offset=offset)
    return [DummyModelDTO.model_validate(row) for row in instances]


@router.put("/")
async def create_dummy_model(
    payload: DummyModelInputDTO,
    service: DummyServiceDep,
) -> DummyModelDTO:
    """Create a new dummy row and return its DTO."""
    instance = await service.create_dummy(name=payload.name)
    return DummyModelDTO.model_validate(instance)
