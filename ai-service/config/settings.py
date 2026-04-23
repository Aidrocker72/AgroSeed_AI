from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application settings
    app_name: str = "AgroSeed AI Service"
    debug: bool = False
    version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # Model settings
    model_storage_path: str = "./models"
    default_forecast_period: int = 30 # days
    supported_forecast_periods: list[int] = [7, 14, 30]
    
    # External services
    etl_service_url: str = "http://etl-service:8000"
    
    # Processing settings
    max_concurrent_requests: int = 10
    request_timeout: int = 60
    
    class Config:
        env_file = ".env"


settings = Settings()