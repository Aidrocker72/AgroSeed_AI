from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from database.connection import engine
from database import models
from routers import auth, territories, forecast


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    root_path=settings.api_prefix,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(territories.router, prefix="/territories", tags=["Territories"])
app.include_router(forecast.router, prefix="/forecast", tags=["Forecasts"])


@app.get("/")
async def root():
    return {"message": "AgroSeed AI Backend API", "version": settings.version}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend-api"}