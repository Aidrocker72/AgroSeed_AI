import pytest
from httpx import AsyncClient
from main import app
from database.connection import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import User
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/register", json={
            "email": "test@example.com",
            "password": "testpassword123"
        })
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login_user():
    # First register a user
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/auth/register", json={
            "email": "login_test@example.com",
            "password": "testpassword123"
        })
        
        # Then try to login
        response = await ac.post("/auth/login", data={
            "username": "login_test@example.com",
            "password": "testpassword123"
        })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token():
    # Register and login to get tokens
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/auth/register", json={
            "email": "refresh_test@example.com",
            "password": "testpassword123"
        })
        
        login_response = await ac.post("/auth/login", data={
            "username": "refresh_test@example.com",
            "password": "testpassword123"
        })
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        # Try to refresh token
        response = await ac.post("/auth/refresh", headers={
            "Authorization": f"Bearer {access_token}"
        })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"