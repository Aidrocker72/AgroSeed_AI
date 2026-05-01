from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import Territory

TERRITORIES = [
    "Краснодарский край",
    "Ростовская область",
    "Ставропольский край",
    "Воронежская область",
    "Саратовская область",
]


async def seed_territories(db: AsyncSession) -> None:
    result = await db.execute(select(Territory))
    if result.scalars().first() is not None:
        return

    for name in TERRITORIES:
        db.add(Territory(name=name))
    await db.commit()
