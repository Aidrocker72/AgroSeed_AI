import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_train_model():
    # Sample training data
    training_data = {
        "seed_data": [
            {
                "name": "Пшеница",
                "price": 15000,
                "date": "2023-01-01"
            },
            {
                "name": "Пшеница",
                "price": 15200,
                "date": "2023-01-02"
            }
        ],
        "news_data": [
            {
                "title": "Новость о погоде",
                "content": "Содержание новости",
                "date": "2023-01-01"
            }
        ],
        "forecast_period": 7
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/predict/train", json=training_data)
    assert response.status_code == 200
    data = response.json()
    assert "model_type" in data
    assert "training_samples" in data
    assert "test_samples" in data
    assert "mae" in data
    assert "mse" in data
    assert "rmse" in data


@pytest.mark.asyncio
async def test_predict():
    # Sample prediction data
    prediction_data = {
        "seed_data": [
            {
                "name": "Кукуруза",
                "price": 18000,
                "date": "2023-01-01"
            },
            {
                "name": "Кукуруза",
                "price": 18200,
                "date": "2023-01-02"
            }
        ],
        "news_data": [
            {
                "title": "Рынок зерна",
                "content": "Анализ рынка",
                "date": "2023-01-01"
            }
        ],
        "forecast_period": 7
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/predict/predict", json=prediction_data)
    assert response.status_code == 200
    data = response.json()
    assert "forecast" in data
    assert "confidence_interval" in data
    assert "model_info" in data
    assert len(data["forecast"]) == 7