from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Territory
from repositories.base import BaseRepository
from sqlalchemy.future import select


class TerritoryRepository(BaseRepository[Territory]):
    def __init__(self):
        super().__init__(Territory)

    async def get_all(self, db: AsyncSession) -> List[Territory]:
        stmt = select(Territory)
        result = await db.execute(stmt)
        return result.scalars().all()
        
    async def get_by_name(self, db: AsyncSession, name: str) -> Territory:
        stmt = select(Territory).where(Territory.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()