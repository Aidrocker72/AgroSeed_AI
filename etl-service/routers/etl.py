from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List
from database.connection import get_db_session
from repositories.seed_data import SeedDataRepository
from repositories.news import NewsRepository
from services.scheduler import SchedulerService


router = APIRouter()
scheduler_service = SchedulerService()
seed_data_repo = SeedDataRepository()
news_repo = NewsRepository()


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


@router.get("/status")
async def get_scheduler_status():
    return {
        "status": "running",
        "jobs": [
            {"id": "collect_seeds", "name": "Collect seed data", "interval": "every 6h"},
            {"id": "collect_news", "name": "Collect news data", "interval": "every 4h"},
        ],
    }
