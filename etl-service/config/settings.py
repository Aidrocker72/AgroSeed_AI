from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database settings
    database_url: str = "postgresql+asyncpg://user:password@localhost/agroseed_etl"
    database_echo: bool = False
    
    # External data sources
    seeds_api_url: Optional[str] = None
    news_rss_url: str = "https://rss.example.com/news"
    
    # Application settings
    app_name: str = "AgroSeed AI ETL Service"
    debug: bool = False
    version: str = "1.0"
    api_prefix: str = "/api/v1"
    
    # Scheduler settings
    scheduler_enabled: bool = True
    seeds_collection_interval: str = "0 */6 * * *"  # Every 6 hours
    news_collection_interval: str = "0 */4 * * *"   # Every 4 hours
    
    # Processing settings
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    
    class Config:
        env_file = ".env"


settings = Settings()