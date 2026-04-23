import pytest
from unittest.mock import AsyncMock, MagicMock
from services.data_collector import DataCollectorService
from database.models import SeedData, News


@pytest.mark.asyncio
async def test_collect_seed_data():
    # Создаем мок для DataCollectorService
    with DataCollectorService() as collector:
        # Проверяем, что метод возвращает список объектов SeedData
        result = await collector.collect_seed_data()
        
        # Проверяем, что результат - это список
        assert isinstance(result, list)
        
        # Если список не пустой, проверяем тип элементов
        if result:
            assert all(isinstance(item, SeedData) for item in result)


@pytest.mark.asyncio
async def test_collect_news_data():
    # Создаем мок для DataCollectorService
    with DataCollectorService() as collector:
        # Проверяем, что метод возвращает список объектов News
        result = await collector.collect_news_data()
        
        # Проверяем, что результат - это список
        assert isinstance(result, list)
        
        # Если список не пустой, проверяем тип элементов
        if result:
            assert all(isinstance(item, News) for item in result)


@pytest.mark.asyncio
async def test_collect_and_store_all():
    # Тестируем полный процесс сбора и сохранения данных
    with DataCollectorService() as collector:
        # Мокаем методы сохранения, чтобы не обращаться к базе данных
        collector.save_seed_data = AsyncMock()
        collector.save_news_data = AsyncMock()
        
        result = await collector.collect_and_store_all()
        
        # Проверяем, что результат содержит ожидаемые ключи
        assert "seed_data_count" in result
        assert "news_count" in result
        assert "timestamp" in result
        
        # Проверяем, что методы сохранения были вызваны
        collector.save_seed_data.assert_called()
        collector.save_news_data.assert_called()