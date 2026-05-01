from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from database.connection import engine, AsyncSessionLocal
from database import models
from routers import auth, territories, forecast
from services.seed import seed_territories


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await seed_territories(db)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = settings.api_prefix
app.include_router(auth.router, prefix=f"{prefix}/auth", tags=["Authentication"])
app.include_router(territories.router, prefix=f"{prefix}/territories", tags=["Territories"])
app.include_router(forecast.router, prefix=f"{prefix}/forecast", tags=["Forecasts"])


@app.get("/")
async def root():
    return {"message": "AgroSeed AI Backend API", "version": settings.version}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend-api"}