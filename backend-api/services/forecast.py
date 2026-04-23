from typing import List, Optional, Dict, Any
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.forecast import ForecastRepository
from database.models import Forecast
from schemas.forecast import ForecastCreate, ForecastUpdate
from config.settings import settings


class ForecastService:
    def __init__(self):
        self.forecast_repository = ForecastRepository()

    async def get_forecast(self, db: AsyncSession, forecast_id: int) -> Optional[Forecast]:
        return await self.forecast_repository.get(db, forecast_id)

    async def get_user_forecasts(
        self, 
        db: AsyncSession, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Forecast]:
        return await self.forecast_repository.get_by_user(db, user_id, skip, limit)

    async def get_user_territory_forecasts(
        self, 
        db: AsyncSession, 
        user_id: int, 
        territory_id: int
    ) -> List[Forecast]:
        return await self.forecast_repository.get_by_user_and_territory(
            db, user_id, territory_id
        )

    async def create_forecast(self, db: AsyncSession, forecast_data: ForecastCreate) -> Forecast:
        forecast = Forecast(
            user_id=forecast_data.user_id,
            territory_id=forecast_data.territory_id,
            raw_data=forecast_data.raw_data,
            ai_result=forecast_data.ai_result
        )
        return await self.forecast_repository.create(db, forecast)

    async def update_forecast(self, db: AsyncSession, forecast_id: int, forecast_data: ForecastUpdate) -> Optional[Forecast]:
        update_data = forecast_data.dict(exclude_unset=True)
        return await self.forecast_repository.update(db, forecast_id, update_data)

    async def delete_forecast(self, db: AsyncSession, forecast_id: int) -> bool:
        return await self.forecast_repository.delete(db, forecast_id)

    async def run_ai_prediction(self, seed_data: Dict[str, Any], news_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Вызов AI сервиса для получения прогноза
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ai_service_url}/predict",
                json={
                    "seed_data": seed_data,
                    "news_data": news_data
                },
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def run_etl_process(self, process_type: str) -> Dict[str, Any]:
        """
        Вызов ETL сервиса для обновления данных
        """
        async with httpx.AsyncClient() as client:
            endpoint = f"{settings.etl_service_url}/etl/run/{process_type}"
            response = await client.get(endpoint, timeout=30.0)
            response.raise_for_status()
            return response.json()