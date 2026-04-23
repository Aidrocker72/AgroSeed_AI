from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import date


class SeedDataInput(BaseModel):
    name: str
    price: float
    date: date


class NewsInput(BaseModel):
    title: str
    content: str
    date: date


class PredictionInput(BaseModel):
    seed_data: List[SeedDataInput]
    news_data: List[NewsInput]
    forecast_period: int = 30 # in days


class PredictionOutput(BaseModel):
    forecast: List[Dict[str, Any]]
    confidence_interval: Optional[Dict[str, Any]]
    model_info: Dict[str, Any]
    execution_time: float