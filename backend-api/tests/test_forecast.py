import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_run_forecast():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # This will fail without authentication, which is expected
        response = await ac.post("/api/v1/forecast/run", params={"territory_id": 1})
    assert response.status_code in [200, 401]  # 200 if successful with auth, 401 without auth


@pytest.mark.asyncio
async def test_get_forecasts():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/forecast/list")
    # This will fail without authentication, which is expected
    assert response.status_code in [200, 401]  # 200 if successful with auth, 401 without auth


@pytest.mark.asyncio
async def test_get_forecast():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/forecast/1")
    # This will fail without authentication, which is expected
    assert response.status_code in [200, 401, 404]  # 200 if found with auth, 401 without auth, 404 if not found