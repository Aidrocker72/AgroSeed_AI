from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Forecast
from repositories.base import BaseRepository
from sqlalchemy.future import select


class ForecastRepository(BaseRepository[Forecast]):
    def __init__(self):
        super().__init__(Forecast)

    async def get_by_user(
        self, 
        db: AsyncSession, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Forecast]:
        stmt = select(Forecast).where(Forecast.user_id == user_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_user_and_territory(
        self, 
        db: AsyncSession, 
        user_id: int, 
        territory_id: int
    ) -> List[Forecast]:
        stmt = select(Forecast).where(
            Forecast.user_id == user_id,
            Forecast.territory_id == territory_id
        )
        result = await db.execute(stmt)
        return result.scalars().all()