import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_run_seed_collection():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/etl/run/seeds")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
    assert "result" in data


@pytest.mark.asyncio
async def test_run_news_collection():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/etl/run/news")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
    assert "result" in data


@pytest.mark.asyncio
async def test_get_scheduler_status():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/etl/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "running"
    assert "jobs" in data
    assert isinstance(data["jobs"], list)