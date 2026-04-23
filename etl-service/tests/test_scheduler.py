import pytest
from unittest.mock import AsyncMock
from services.scheduler import SchedulerService


@pytest.mark.asyncio
async def test_scheduler_service_initialization():
    # Проверяем инициализацию сервиса планировщика
    scheduler_service = SchedulerService()
    
    # Проверяем, что планировщик и коллекционер данных инициализированы
    assert scheduler_service.scheduler is not None
    assert scheduler_service.data_collector is not None


@pytest.mark.asyncio
async def test_run_once_seed_collection():
    # Тестируем однократный запуск сбора данных о семенах
    scheduler_service = SchedulerService()
    
    # Мокаем метод коллекционера
    scheduler_service.data_collector.collect_and_store_all = AsyncMock(return_value={
        "seed_data_count": 10,
        "news_count": 5,
        "timestamp": "2023-01-01T00:00:00"
    })
    
    result = await scheduler_service.run_once_seed_collection()
    
    # Проверяем, что результат содержит ожидаемые данные
    assert "seed_data_count" in result
    assert "news_count" in result
    assert "timestamp" in result
    
    # Проверяем, что метод коллекционера был вызван
    scheduler_service.data_collector.collect_and_store_all.assert_called_once()


@pytest.mark.asyncio
async def test_run_once_news_collection():
    # Тестируем однократный запуск сбора новостей
    scheduler_service = SchedulerService()
    
    # Мокаем метод коллекционера
    scheduler_service.data_collector.collect_and_store_all = AsyncMock(return_value={
        "seed_data_count": 8,
        "news_count": 12,
        "timestamp": "2023-01-01T00:00:00"
    })
    
    result = await scheduler_service.run_once_news_collection()
    
    # Проверяем, что результат содержит ожидаемые данные
    assert "seed_data_count" in result
    assert "news_count" in result
    assert "timestamp" in result
    
    # Проверяем, что метод коллекционера был вызван
    scheduler_service.data_collector.collect_and_store_all.assert_called_once()