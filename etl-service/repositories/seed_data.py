from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
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
        end_date: str,
    ) -> List[SeedData]:
        stmt = select(SeedData).where(
            SeedData.territory_id == territory_id,
            SeedData.date >= start_date,
            SeedData.date <= end_date,
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_seed_data_batch(self, db: AsyncSession, seed_data_list: List[SeedData]) -> int:
        if not seed_data_list:
            return 0
        stmt = (
            pg_insert(SeedData)
            .values([
                {
                    "territory_id": sd.territory_id,
                    "name": sd.name,
                    "price": sd.price,
                    "date": sd.date,
                }
                for sd in seed_data_list
            ])
            .on_conflict_do_nothing(
                index_elements=["territory_id", "name", "date"]
            )
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount
