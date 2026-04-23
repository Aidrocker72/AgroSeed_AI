import pytest
from models.predictor import PricePredictor
from datetime import datetime, timedelta
from unittest.mock import patch


@pytest.fixture
def sample_seed_data():
    """Создает тестовые данные о ценах на семена"""
    base_date = datetime.now() - timedelta(days=30)
    return [
        {
            "name": "Пшеница",
            "price": 15000 + i * 100,  # Небольшой тренд вверх
            "date": (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        }
        for i in range(30)
    ]


@pytest.fixture
def sample_news_data():
    """Создает тестовые данные о новостях"""
    base_date = datetime.now() - timedelta(days=10)
    return [
        {
            "title": f"Новость о погоде {i}",
            "content": f"Содержание новости о погоде {i}",
            "date": (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
        }
        for i in range(10)
    ]


def test_predictor_initialization():
    """Тест инициализации модели"""
    predictor = PricePredictor()
    assert predictor is not None
    assert not predictor.is_trained


def test_prepare_data(sample_seed_data, sample_news_data):
    """Тест подготовки данных"""
    predictor = PricePredictor()
    df = predictor._prepare_data(sample_seed_data, sample_news_data)
    
    assert df is not None
    assert len(df) > 0
    assert 'price' in df.columns
    assert 'date' in df.columns


def test_train_model(sample_seed_data, sample_news_data):
    """Тест обучения модели"""
    predictor = PricePredictor()
    
    # Обучаем модель
    result = predictor.train(sample_seed_data, sample_news_data)
    
    # Проверяем результат обучения
    assert result is not None
    assert 'mae' in result
    assert 'mse' in result
    assert 'rmse' in result
    assert predictor.is_trained


def test_predict_model(sample_seed_data, sample_news_data):
    """Тест предсказания модели"""
    predictor = PricePredictor()
    
    # Сначала обучаем модель
    predictor.train(sample_seed_data, sample_news_data)
    
    # Выполняем предсказание
    result = predictor.predict(sample_seed_data, sample_news_data, forecast_period=7)
    
    # Проверяем результат предсказания
    assert result is not None
    assert 'forecast' in result
    assert 'confidence_interval' in result
    assert 'model_info' in result
    assert len(result['forecast']) == 7


def test_predict_with_different_periods(sample_seed_data, sample_news_data):
    """Тест предсказания с разными периодами"""
    predictor = PricePredictor()
    
    # Обучаем модель
    predictor.train(sample_seed_data, sample_news_data)
    
    # Проверяем предсказания для разных периодов
    for period in [7, 14, 30]:
        result = predictor.predict(sample_seed_data, sample_news_data, forecast_period=period)
        assert len(result['forecast']) == period


def test_save_and_load_model(sample_seed_data, sample_news_data, tmp_path):
    """Тест сохранения и загрузки модели"""
    # Используем временный путь для тестирования
    model_path = tmp_path / "test_model"
    model_path.mkdir()
    
    predictor = PricePredictor(model_storage_path=str(model_path))
    
    # Обучаем модель
    predictor.train(sample_seed_data, sample_news_data)
    
    # Сохраняем модель
    saved_path = predictor.save_model("test_model")
    
    # Создаем новую модель и загружаем
    new_predictor = PricePredictor(model_storage_path=str(model_path))
    new_predictor.load_model("test_model")
    
    # Проверяем, что новая модель загружена и обучена
    assert new_predictor.is_trained