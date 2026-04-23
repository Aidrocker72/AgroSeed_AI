from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any


class ForecastBase(BaseModel):
    territory_id: int
    raw_data: Dict[str, Any]
    ai_result: Dict[str, Any]


class ForecastCreate(ForecastBase):
    pass


class ForecastUpdate(BaseModel):
    raw_data: Optional[Dict[str, Any]] = None
    ai_result: Optional[Dict[str, Any]] = None


class ForecastResponse(ForecastBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True