from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import SeedData
from repositories.base import BaseRepository
from sqlalchemy.future import select


class SeedDataRepository(BaseRepository[SeedData]):
    def __init__(self):
        super().__init__(SeedData)

    async def get_by_territory(
        self,
        db: AsyncSession,
        territory_id: int,
        skip: int = 0,
        limit: int = 100,
        crop_name: str = None,
    ) -> List[SeedData]:
        stmt = select(SeedData).where(SeedData.territory_id == territory_id)
        if crop_name:
            stmt = stmt.where(SeedData.name == crop_name)
        stmt = stmt.order_by(SeedData.date).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_territory_and_date_range(
        self, 
        db: AsyncSession, 
        territory_id: int, 
        start_date: str, 
        end_date: str
    ) -> List[SeedData]:
        stmt = select(SeedData).where(
            SeedData.territory_id == territory_id,
            SeedData.date >= start_date,
            SeedData.date <= end_date
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_seed_data_batch(self, db: AsyncSession, seed_data_list: List[SeedData]) -> List[SeedData]:
        for seed_data in seed_data_list:
            db.add(seed_data)
        await db.commit()
        for seed_data in seed_data_list:
            await db.refresh(seed_data)
        return seed_data_list