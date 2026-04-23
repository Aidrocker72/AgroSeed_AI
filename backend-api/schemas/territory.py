from pydantic import BaseModel
from typing import Optional


class TerritoryBase(BaseModel):
    name: str


class TerritoryCreate(TerritoryBase):
    pass


class TerritoryUpdate(BaseModel):
    name: Optional[str] = None


class TerritoryResponse(TerritoryBase):
    id: int

    class Config:
        from_attributes = True