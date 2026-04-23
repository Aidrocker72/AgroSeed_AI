from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from services.data_collector import DataCollectorService
from services.scheduler import SchedulerService


router = APIRouter()
scheduler_service = SchedulerService()


@router.get("/run/seeds")
async def run_seed_collection():
    """
    Ручной запуск сбора данных о семенах
    """
    try:
        result = await scheduler_service.run_once_seed_collection()
        return {
            "status": "success",
            "message": "Seed data collection completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting seed data: {str(e)}")


@router.get("/run/news")
async def run_news_collection():
    """
    Ручной запуск сбора новостей
    """
    try:
        result = await scheduler_service.run_once_news_collection()
        return {
            "status": "success",
            "message": "News collection completed",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting news: {str(e)}")


@router.get("/status")
async def get_scheduler_status():
    """
    Получение статуса планировщика
    """
    # В реальной реализации здесь будет проверка статуса планировщика
    # Пока что возвращаем заглушку
    return {
        "status": "running",
        "message": "Scheduler is running",
        "jobs": [
            {"id": "collect_seeds", "name": "Collect seed data", "next_run": "2023-01-01T06:00:00"},
            {"id": "collect_news", "name": "Collect news data", "next_run": "2023-01-01T04:00:00"}
        ]
    }