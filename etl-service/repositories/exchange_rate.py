from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from database.models import ExchangeRate
from repositories.base import BaseRepository


class ExchangeRateRepository(BaseRepository[ExchangeRate]):
    def __init__(self):
        super().__init__(ExchangeRate)

    async def get_recent(
        self, db: AsyncSession, currency: str = "USD", limit: int = 90
    ) -> List[ExchangeRate]:
        stmt = (
            select(ExchangeRate)
            .where(ExchangeRate.currency == currency)
            .order_by(ExchangeRate.date.asc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def upsert_batch(self, db: AsyncSession, rates: List[ExchangeRate]) -> None:
        if not rates:
            return
        stmt = (
            pg_insert(ExchangeRate)
            .values([
                {"currency": r.currency, "date": r.date, "rate": r.rate}
                for r in rates
            ])
            .on_conflict_do_nothing(index_elements=["currency", "date"])
        )
        await db.execute(stmt)
        await db.commit()
