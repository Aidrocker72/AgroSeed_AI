from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Database settings
    database_url: str = "postgresql+asyncpg://user:password@localhost/agroseed"
    database_echo: bool = False

    # JWT settings — SECRET_KEY must be set via environment variable
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # OAuth2 settings
    oauth2_enabled: bool = True
    oauth2_client_id: Optional[str] = None
    oauth2_client_secret: Optional[str] = None
    oauth2_redirect_uri: Optional[str] = None

    # CORS — comma-separated list of allowed origins, e.g. "http://localhost:3000"
    cors_origins: List[str] = ["http://localhost:3000"]

    # External services
    etl_service_url: str = "http://etl-service:8000"
    ai_service_url: str = "http://ai-service:8000"

    # Application settings
    app_name: str = "AgroSeed AI Backend API"
    debug: bool = False
    version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    # Internationalization
    default_language: str = "en"
    supported_languages: List[str] = ["en", "ru"]

    class Config:
        env_file = ".env"


settings = Settings()