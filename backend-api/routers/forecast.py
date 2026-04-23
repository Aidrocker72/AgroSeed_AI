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
    current_user: User = Depends(jwt_auth.get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    # In a real implementation, we would gather seed and news data
    # and send it to the AI service for prediction
    # For now, we'll simulate the process
    
    # Run ETL to get latest data
    await forecast_service.run_etl_process("seeds")
    await forecast_service.run_etl_process("news")
    
    # Get data for prediction (in real implementation, this would come from the database)
    seed_data = {"territory_id": territory_id, "historical_data": []}
    news_data = {"territory_id": territory_id, "recent_news": []}
    
    # Call AI service for prediction
    ai_result = await forecast_service.run_ai_prediction(seed_data, news_data)
    
    # Create forecast record
    forecast_data = ForecastCreate(
        user_id=current_user.id,
        territory_id=territory_id,
        raw_data={"seed_data": seed_data, "news_data": news_data},
        ai_result=ai_result
    )
    
    forecast = await forecast_service.create_forecast(db, forecast_data)
    return forecast


@router.get("/list", response_model=list[ForecastResponse])
async def get_forecasts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(jwt_auth.get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    forecasts = await forecast_service.get_user_forecasts(db, current_user.id, skip, limit)
    return forecasts


@router.get("/{forecast_id}", response_model=ForecastResponse)
async def get_forecast(
    forecast_id: int,
    current_user: User = Depends(jwt_auth.get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    forecast = await forecast_service.get_forecast(db, forecast_id)
    if not forecast or forecast.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forecast not found"
        )
    return forecast