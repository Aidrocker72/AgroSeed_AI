import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_get_territories():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/territories/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_territory_by_id():
    # First create a territory
    async with AsyncClient(app=app, base_url="http://test") as ac:
        create_response = await ac.post("/territories/", json={
            "name": "Test Territory"
        })
        assert create_response.status_code == 200
        territory_data = create_response.json()
        territory_id = territory_data["id"]
        
        # Then get the territory by ID
        response = await ac.get(f"/territories/{territory_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == territory_id
    assert data["name"] == "Test Territory"


@pytest.mark.asyncio
async def test_create_territory():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/territories/", json={
            "name": "New Test Territory"
        })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == "New Test Territory"


@pytest.mark.asyncio
async def test_update_territory():
    # First create a territory
    async with AsyncClient(app=app, base_url="http://test") as ac:
        create_response = await ac.post("/territories/", json={
            "name": "Original Territory Name"
        })
        assert create_response.status_code == 200
        territory_data = create_response.json()
        territory_id = territory_data["id"]
        
        # Then update the territory
        update_response = await ac.put(f"/territories/{territory_id}", json={
            "name": "Updated Territory Name"
        })
        assert update_response.status_code == 200
        updated_data = update_response.json()
        assert updated_data["id"] == territory_id
        assert updated_data["name"] == "Updated Territory Name"


@pytest.mark.asyncio
async def test_delete_territory():
    # First create a territory
    async with AsyncClient(app=app, base_url="http://test") as ac:
        create_response = await ac.post("/territories/", json={
            "name": "Territory to Delete"
        })
        assert create_response.status_code == 200
        territory_data = create_response.json()
        territory_id = territory_data["id"]
        
        # Then delete the territory
        delete_response = await ac.delete(f"/territories/{territory_id}")
        assert delete_response.status_code == 200
        assert delete_response.json() == {"message": "Territory deleted successfully"}
        
        # Verify the territory is gone
        get_response = await ac.get(f"/territories/{territory_id}")
        assert get_response.status_code == 404