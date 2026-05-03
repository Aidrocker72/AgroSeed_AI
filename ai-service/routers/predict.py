from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time
from models.predictor import PricePredictor
from schemas.prediction import PredictionInput, PredictionOutput
from config.settings import settings


router = APIRouter()
predictor = PricePredictor(model_storage_path=settings.model_storage_path)


@router.post("/predict", response_model=PredictionOutput)
async def predict_price(input_data: PredictionInput) -> Dict[str, Any]:
    if input_data.forecast_period not in settings.supported_forecast_periods:
        raise HTTPException(
            status_code=400,
            detail=f"Период {input_data.forecast_period} дней не поддерживается. "
                   f"Допустимые: {settings.supported_forecast_periods}",
        )

    try:
        start_time = time.time()

        seed_list  = [item.model_dump() for item in input_data.seed_data]
        news_list  = [item.model_dump() for item in input_data.news_data]
        rates_list = [item.model_dump() for item in input_data.exchange_rates] if input_data.exchange_rates else None
        oil_list   = [item.model_dump() for item in input_data.oil_prices] if input_data.oil_prices else None

        # Всегда переобучаем — каждый запрос может содержать данные другой культуры
        predictor.train(seed_list, news_list, exchange_rates=rates_list, oil_prices=oil_list)

        result = predictor.predict(
            seed_data=seed_list,
            news_data=news_list,
            forecast_period=input_data.forecast_period,
            exchange_rates=rates_list,
            oil_prices=oil_list,
        )

        return {
            "forecast": result["forecast"],
            "confidence_interval": result["confidence_interval"],
            "model_info": result["model_info"],
            "execution_time": time.time() - start_time,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка прогноза: {str(e)}")


@router.post("/train")
async def train_model(input_data: PredictionInput) -> Dict[str, Any]:
    """
    Обучение модели на предоставленных данных
    """
    try:
        start_time = time.time()
        
        # Выполняем обучение
        result = predictor.train(
            seed_data=[item.model_dump() for item in input_data.seed_data],
            news_data=[item.model_dump() for item in input_data.news_data],
        )
        
        execution_time = time.time() - start_time
        
        # Сохраняем обученную модель
        model_path = predictor.save_model()
        
        result["execution_time"] = execution_time
        result["model_saved_to"] = model_path
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обучении модели: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Проверка работоспособности сервиса
    """
    return {
        "status": "healthy",
        "service": "ai-service",
        "model_loaded": predictor.is_trained
    }