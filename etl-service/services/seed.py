import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import Territory, SeedData

TERRITORIES = [
    "Краснодарский край",
    "Ростовская область",
    "Ставропольский край",
    "Воронежская область",
    "Саратовская область",
]

SEEDS = [
    ("Пшеница",  15000.00),
    ("Кукуруза", 18000.00),
    ("Соя",      22000.00),
    ("Подсолнечник", 28000.00),
    ("Ячмень",   12000.00),
]

DAYS = 90


def _generate_prices(base: float, days: int) -> list[float]:
    """Random walk around base price (±15% total drift)."""
    prices = []
    price = base
    for _ in range(days):
        price *= 1 + random.gauss(0, 0.008)
        price = max(price, base * 0.7)
        prices.append(round(price, 2))
    return prices


async def seed_etl_data(db: AsyncSession) -> None:
    result = await db.execute(select(Territory))
    territories = result.scalars().all()

    if not territories:
        for name in TERRITORIES:
            db.add(Territory(name=name))
        await db.flush()
        result = await db.execute(select(Territory))
        territories = result.scalars().all()

    # Check if price data already exists
    sd_result = await db.execute(select(SeedData).limit(1))
    if sd_result.scalars().first() is not None:
        await db.commit()
        return

    now = datetime.now(timezone.utc)
    for territory in territories:
        for seed_name, base_price in SEEDS:
            prices = _generate_prices(base_price, DAYS)
            for i, price in enumerate(prices):
                date = now - timedelta(days=DAYS - i)
                db.add(SeedData(
                    territory_id=territory.id,
                    name=seed_name,
                    price=price,
                    date=date,
                ))

    await db.commit()
