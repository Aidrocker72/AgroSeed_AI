from fastapi import FastAPI
from config.settings import settings
from routers import predict


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    root_path=settings.api_prefix
)


# Include routers
app.include_router(predict.router, prefix="/predict", tags=["Prediction"])


@app.get("/")
async def root():
    return {"message": "AgroSeed AI Service", "version": settings.version}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-service"}