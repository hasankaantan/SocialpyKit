"""Integration tests for the dummy demo endpoints."""

import uuid

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.models.dummy_model import DummyModel
from app.repositories.dummy import DummyRepository


async def test_creation(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """PUT /dummy/ persists a new row and returns its DTO."""
    url = fastapi_app.url_path_for("create_dummy_model")
    test_name = uuid.uuid4().hex

    response = await client.put(url, json={"name": test_name})

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["name"] == test_name

    repository = DummyRepository(dbsession)
    rows = await repository.find_by_name(test_name)
    assert len(rows) == 1
    assert rows[0].name == test_name


async def test_getting(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """GET /dummy/ returns rows previously seeded through the repository."""
    repository = DummyRepository(dbsession)
    test_name = uuid.uuid4().hex

    assert await repository.list() == []

    await repository.create(DummyModel(name=test_name))
    await dbsession.commit()

    url = fastapi_app.url_path_for("get_dummy_models")
    response = await client.get(url)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == test_name
