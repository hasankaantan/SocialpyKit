"""Integration tests for the monitoring endpoints."""

from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status


async def test_health_endpoint_returns_ok_when_db_is_reachable(
    client: AsyncClient,
    fastapi_app: FastAPI,
) -> None:
    """GET /api/health pings postgres and reports status=ok on success."""
    url = fastapi_app.url_path_for("health_check")

    response = await client.get(url)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body == {"status": "ok", "database": "ok"}
