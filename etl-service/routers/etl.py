from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List
from database.connection import get_db_session
from repositories.seed_data import SeedDataRepository
from repositories.news import NewsRepository
from repositories.etl_run import ETLRunRepository
from repositories.exchange_rate import ExchangeRateRepository
from services.scheduler import SchedulerService


router = APIRouter()
scheduler_service = SchedulerService()
seed_data_repo = SeedDataRepository()
news_repo = NewsRepository()
etl_run_repo = ETLRunRepository()
exchange_rate_repo = ExchangeRateRepository()


@router.get("/run/seeds")
async def run_seed_collection():
    try:
        result = await scheduler_service.run_once_seed_collection()
        return {"status": "success", "message": "Seed data collection completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting seed data: {str(e)}")


@router.get("/run/news")
async def run_news_collection():
    try:
        result = await scheduler_service.run_once_news_collection()
        return {"status": "success", "message": "News collection completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting news: {str(e)}")


@router.get("/data/seeds/{territory_id}", response_model=List[Any])
async def get_seed_data(
    territory_id: int,
    limit: int = 100,
    crop_name: str = None,
    db: AsyncSession = Depends(get_db_session),
):
    records = await seed_data_repo.get_by_territory(db, territory_id, limit=limit, crop_name=crop_name)
    return [
        {
            "id": r.id,
            "territory_id": r.territory_id,
            "name": r.name,
            "price": float(r.price),
            "date": r.date.date().isoformat(),
        }
        for r in records
    ]


@router.get("/data/news/{territory_id}", response_model=List[Any])
async def get_news_data(
    territory_id: int,
    limit: int = 20,
    db: AsyncSession = Depends(get_db_session),
):
    records = await news_repo.get_by_territory(db, territory_id, limit=limit)
    return [
        {
            "id": r.id,
            "territory_id": r.territory_id,
            "title": r.title,
            "content": r.content,
            "date": r.date.date().isoformat(),
        }
        for r in records
    ]


@router.get("/data/exchange-rate", response_model=List[Any])
async def get_exchange_rates(
    currency: str = "USD",
    limit: int = 90,
    db: AsyncSession = Depends(get_db_session),
):
    rates = await exchange_rate_repo.get_recent(db, currency=currency, limit=limit)
    return [
        {"date": r.date.date().isoformat(), "rate": float(r.rate)}
        for r in rates
    ]


@router.get("/history")
async def get_etl_history(limit: int = 20, db: AsyncSession = Depends(get_db_session)):
    runs = await etl_run_repo.get_recent(db, limit=limit)
    return [
        {
            "id": r.id,
            "started_at": r.started_at.isoformat(),
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "status": r.status,
            "seed_data_count": r.seed_data_count,
            "news_count": r.news_count,
            "data_source": r.data_source,
            "error": r.error,
        }
        for r in runs
    ]


@router.get("/status")
async def get_scheduler_status(db: AsyncSession = Depends(get_db_session)):
    last_run = await etl_run_repo.get_last(db)
    return {
        "status": "running",
        "jobs": [
            {"id": "collect_seeds", "name": "Collect seed data", "interval": "every 6h"},
            {"id": "collect_news", "name": "Collect news data", "interval": "every 4h"},
        ],
        "last_run": {
            "timestamp": last_run.started_at.isoformat(),
            "status": last_run.status,
            "data_source": last_run.data_source,
            "seed_data_count": last_run.seed_data_count,
        } if last_run else None,
    }
