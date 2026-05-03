from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from schemas.forecast import ForecastResponse, ForecastCreate
from services.forecast import ForecastService
from auth.jwt import JWTAuth
from database.models import User


router = APIRouter()
forecast_service = ForecastService()
jwt_auth = JWTAuth()


@router.post("/run", response_model=ForecastResponse)
async def run_forecast(
    territory_id: int,
    crop_name: str = "Пшеница",
    forecast_period: int = 30,
    current_user: User = Depends(jwt_auth.get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    seed_data = await forecast_service.get_seed_data(territory_id, crop_name=crop_name)
    if not seed_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Нет данных по культуре '{crop_name}' для территории {territory_id}.",
        )

    news_data      = await forecast_service.get_news_data(territory_id)
    exchange_rates = await forecast_service.get_exchange_rates()
    oil_prices     = await forecast_service.get_oil_prices()

    ai_result = await forecast_service.run_ai_prediction(
        seed_data, news_data,
        forecast_period=forecast_period,
        exchange_rates=exchange_rates,
        oil_prices=oil_prices,
    )

    forecast_data = ForecastCreate(
        user_id=current_user.id,
        territory_id=territory_id,
        raw_data={
            "crop_name": crop_name,
            "forecast_period": forecast_period,
            "seed_data_count": len(seed_data),
            "news_count": len(news_data),
        },
        ai_result=ai_result,
    )
    return await forecast_service.create_forecast(db, forecast_data)


@router.delete("/{forecast_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_forecast(
    forecast_id: int,
    current_user: User = Depends(jwt_auth.get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    forecast = await forecast_service.get_forecast(db, forecast_id)
    if not forecast or forecast.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forecast not found")
    await forecast_service.delete_forecast(db, forecast_id)


@router.get("/list", response_model=list[ForecastResponse])
async def get_forecasts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(jwt_auth.get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    return await forecast_service.get_user_forecasts(db, current_user.id, skip, limit)


@router.get("/{forecast_id}", response_model=ForecastResponse)
async def get_forecast(
    forecast_id: int,
    current_user: User = Depends(jwt_auth.get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    forecast = await forecast_service.get_forecast(db, forecast_id)
    if not forecast or forecast.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found",
        )
    return forecast
