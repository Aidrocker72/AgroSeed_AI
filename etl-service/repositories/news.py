from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import News
from repositories.base import BaseRepository
from sqlalchemy.future import select


class NewsRepository(BaseRepository[News]):
    def __init__(self):
        super().__init__(News)

    async def get_by_territory(
        self, 
        db: AsyncSession, 
        territory_id: int, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[News]:
        stmt = select(News).where(News.territory_id == territory_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_by_territory_and_date_range(
        self, 
        db: AsyncSession, 
        territory_id: int, 
        start_date: str, 
        end_date: str
    ) -> List[News]:
        stmt = select(News).where(
            News.territory_id == territory_id,
            News.date >= start_date,
            News.date <= end_date
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_news_batch(self, db: AsyncSession, news_list: List[News]) -> List[News]:
        for news_item in news_list:
            db.add(news_item)
        await db.commit()
        for news_item in news_list:
            await db.refresh(news_item)
        return news_list