import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import Territory, SeedData
from config.territories import TERRITORIES

SEEDS = [
    ("Пшеница",      15000.00),
    ("Кукуруза",     18000.00),
    ("Соя",          22000.00),
    ("Подсолнечник", 28000.00),
    ("Ячмень",       12000.00),
]

DAYS = 90


def _generate_prices(base: float, days: int) -> list[float]:
    prices = []
    price = base
    for _ in range(days):
        price *= 1 + random.gauss(0, 0.008)
        price = max(price, base * 0.7)
        prices.append(round(price, 2))
    return prices


async def seed_etl_data(db: AsyncSession) -> None:
    result = await db.execute(select(Territory.name))
    existing_names = set(result.scalars().all())

    missing = [name for name in TERRITORIES if name not in existing_names]
    if missing:
        for name in missing:
            db.add(Territory(name=name))
        await db.flush()

    result = await db.execute(select(Territory))
    territories = result.scalars().all()

    # Генерируем начальные данные только для территорий без цен
    now = datetime.now(timezone.utc)
    for territory in territories:
        sd_result = await db.execute(
            select(SeedData).where(SeedData.territory_id == territory.id).limit(1)
        )
        if sd_result.scalars().first() is not None:
            continue

        for seed_name, base_price in SEEDS:
            for i, price in enumerate(_generate_prices(base_price, DAYS)):
                db.add(SeedData(
                    territory_id=territory.id,
                    name=seed_name,
                    price=price,
                    date=now - timedelta(days=DAYS - i),
                ))

    await db.commit()
