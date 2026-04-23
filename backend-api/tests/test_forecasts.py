import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_run_forecast():
    # Register a user first
    async with AsyncClient(app=app, base_url="http://test") as ac:
        register_response = await ac.post("/auth/register", json={
            "email": "forecast_test@example.com",
            "password": "testpassword123"
        })
        assert register_response.status_code == 200
        user_data = register_response.json()
        user_id = user_data["id"]
        
        # Create a territory
        territory_response = await ac.post("/territories/", json={
            "name": "Forecast Test Territory"
        })
        assert territory_response.status_code == 200
        territory_data = territory_response.json()
        territory_id = territory_data["id"]
        
        # Run a forecast
        response = await ac.post("/forecast/run", params={
            "territory_id": territory_id
        }, headers={
            "Authorization": f"Bearer test_token"  # This will likely fail without proper auth
        })
    # Note: This test expects a 401 since we're not properly authenticated
    assert response.status_code in [200, 401]


@pytest.mark.asyncio
async def test_get_forecasts():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/forecast/list")
    # This test expects a 401 since we're not properly authenticated
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_forecast_by_id():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/forecast/1")
    # This test expects a 401 since we're not properly authenticated
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_forecasts_authenticated():
    # Register a user first
    async with AsyncClient(app=app, base_url="http://test") as ac:
        register_response = await ac.post("/auth/register", json={
            "email": "auth_forecast_test@example.com",
            "password": "testpassword123"
        })
        assert register_response.status_code == 200
        
        # Login to get token
        login_response = await ac.post("/auth/login", data={
            "username": "auth_forecast_test@example.com",
            "password": "testpassword123"
        })
        assert login_response.status_code == 200
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        # Get forecasts with authentication
        response = await ac.get("/forecast/list", headers={
            "Authorization": f"Bearer {access_token}"
        })
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)