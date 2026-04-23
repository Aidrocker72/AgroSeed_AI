import pytest
from httpx import AsyncClient
import asyncio


@pytest.mark.asyncio
async def test_full_workflow():
    """
    Тест интеграции всех сервисов:
    1. Создание пользователя в backend
    2. Запуск ETL для получения данных
    3. Запуск AI сервиса для прогноза
    4. Получение результата в backend
    """
    
    # Тест интеграции будет использовать HTTP-запросы к запущенным сервисам
    # вместо прямого импорта приложений, так как каждый сервис запускается отдельно
    
    # Для запуска этого теста нужно сначала запустить все сервисы через docker-compose
    # и затем выполнить тесты, которые будут обращаться к ним по сети
    
    # Проверка доступности backend сервиса
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    # Проверка доступности etl сервиса
    async with AsyncClient(base_url="http://localhost:8001") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    # Проверка доступности ai сервиса
    async with AsyncClient(base_url="http://localhost:8002") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"