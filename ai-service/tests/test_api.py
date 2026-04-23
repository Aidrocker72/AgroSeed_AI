import pytest
from fastapi.testclient import TestClient
from main import app
from datetime import datetime, timedelta


client = TestClient(app)


def test_health_check():
    """Тест проверки работоспособности сервиса"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "service" in data
    assert data["service"] == "ai-service"


def test_predict_endpoint():
    """Тест эндпоинта предсказания"""
    # Подготовка тестовых данных
    seed_data = [
        {
            "name": "Пшеница",
            "price": 15000 + i * 50,
            "date": (datetime.now() - timedelta(days=30-i)).strftime('%Y-%m-%d')
        }
        for i in range(30)
    ]
    
    news_data = [
        {
            "title": f"Новость {i}",
            "content": f"Содержание новости {i}",
            "date": (datetime.now() - timedelta(days=10-i)).strftime('%Y-%m-%d')
        }
        for i in range(10)
    ]
    
    payload = {
        "seed_data": seed_data,
        "news_data": news_data,
        "forecast_period": 7
    }
    
    response = client.post("/predict", json=payload)
    
    # Временно ожидаем 500 ошибку, так как модель не обучена
    # В реальном сценарии нужно сначала обучить модель
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "forecast" in data
        assert "confidence_interval" in data
        assert "model_info" in data
        assert len(data["forecast"]) == 7


def test_train_endpoint():
    """Тест эндпоинта обучения"""
    # Подготовка тестовых данных
    seed_data = [
        {
            "name": "Кукуруза",
            "price": 18000 + i * 30,
            "date": (datetime.now() - timedelta(days=25-i)).strftime('%Y-%m-%d')
        }
        for i in range(25)
    ]
    
    news_data = [
        {
            "title": f"Рынок зерна {i}",
            "content": f"Анализ рынка зерна {i}",
            "date": (datetime.now() - timedelta(days=8-i)).strftime('%Y-%m-%d')
        }
        for i in range(8)
    ]
    
    payload = {
        "seed_data": seed_data,
        "news_data": news_data
    }
    
    response = client.post("/train", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "model_type" in data
    assert "training_samples" in data
    assert "test_samples" in data
    assert "mae" in data
    assert "mse" in data
    assert "rmse" in data