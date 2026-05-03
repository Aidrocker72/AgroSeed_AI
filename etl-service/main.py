from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.settings import settings
from database.connection import AsyncSessionLocal
from routers import etl
from services.scheduler import SchedulerService
from services.seed import seed_etl_data


scheduler_service = SchedulerService()


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with AsyncSessionLocal() as db:
        await seed_etl_data(db)
    await scheduler_service.start()
    yield
    await scheduler_service.stop()


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(etl.router, prefix="/etl", tags=["ETL Operations"])


@app.get("/")
async def root():
    return {"message": "AgroSeed AI ETL Service", "version": settings.version}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "etl-service"}
