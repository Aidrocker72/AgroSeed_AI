from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import ETLRun
from repositories.base import BaseRepository


class ETLRunRepository(BaseRepository[ETLRun]):
    def __init__(self):
        super().__init__(ETLRun)

    async def get_recent(self, db: AsyncSession, limit: int = 20) -> List[ETLRun]:
        stmt = select(ETLRun).order_by(ETLRun.started_at.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_last(self, db: AsyncSession) -> Optional[ETLRun]:
        stmt = select(ETLRun).order_by(ETLRun.started_at.desc()).limit(1)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_run(
        self,
        db: AsyncSession,
        run_id: int,
        status: str,
        completed_at: datetime,
        seed_data_count: int = 0,
        news_count: int = 0,
        data_source: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Optional[ETLRun]:
        data = {"status": status, "completed_at": completed_at,
                "seed_data_count": seed_data_count, "news_count": news_count}
        if data_source:
            data["data_source"] = data_source
        if error:
            data["error"] = error
        return await self.update(db, run_id, data)
