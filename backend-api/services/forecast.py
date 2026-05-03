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
        forecast = Forecast(**forecast_data.model_dump())
        return await self.forecast_repository.create(db, forecast)

    async def update_forecast(self, db: AsyncSession, forecast_id: int, forecast_data: ForecastUpdate) -> Optional[Forecast]:
        update_data = forecast_data.model_dump(exclude_unset=True)
        return await self.forecast_repository.update(db, forecast_id, update_data)

    async def delete_forecast(self, db: AsyncSession, forecast_id: int) -> bool:
        return await self.forecast_repository.delete(db, forecast_id)

    async def get_seed_data(self, territory_id: int, crop_name: str = None) -> List[Dict[str, Any]]:
        params = {"limit": 200}
        if crop_name:
            params["crop_name"] = crop_name
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.etl_service_url}/etl/data/seeds/{territory_id}",
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_news_data(self, territory_id: int) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.etl_service_url}/etl/data/news/{territory_id}",
                params={"limit": 50},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def _fetch_rate_data(self, currency: str, limit: int = 90) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.etl_service_url}/etl/data/exchange-rate",
                    params={"currency": currency, "limit": limit},
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception:
            return []

    async def get_exchange_rates(self) -> List[Dict[str, Any]]:
        return await self._fetch_rate_data("USD")

    async def get_oil_prices(self) -> List[Dict[str, Any]]:
        return await self._fetch_rate_data("OIL_USD")

    async def run_ai_prediction(
        self,
        seed_data: List[Dict[str, Any]],
        news_data: List[Dict[str, Any]],
        forecast_period: int = 30,
        exchange_rates: Optional[List[Dict[str, Any]]] = None,
        oil_prices: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ai_service_url}/predict/predict",
                json={
                    "seed_data": seed_data,
                    "news_data": news_data,
                    "forecast_period": forecast_period,
                    "exchange_rates": exchange_rates or [],
                    "oil_prices": oil_prices or [],
                },
                timeout=120.0,
            )
            response.raise_for_status()
            return response.json()