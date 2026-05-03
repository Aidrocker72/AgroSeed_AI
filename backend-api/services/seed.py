from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import Territory
from config.territories import TERRITORIES


async def seed_territories(db: AsyncSession) -> None:
    result = await db.execute(select(Territory.name))
    existing = set(result.scalars().all())

    missing = [name for name in TERRITORIES if name not in existing]
    if not missing:
        return

    for name in missing:
        db.add(Territory(name=name))
    await db.commit()
