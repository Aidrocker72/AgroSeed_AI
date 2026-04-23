import aiohttp
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from config.settings import settings
from database.connection import AsyncSessionLocal
from database.models import SeedData, News
from repositories.seed_data import SeedDataRepository
from repositories.news import NewsRepository
from repositories.territory import TerritoryRepository


class DataCollectorService:
    def __init__(self):
        self.seed_data_repo = SeedDataRepository()
        self.news_repo = NewsRepository()
        self.territory_repo = TerritoryRepository()
        self.http_session = None

    async def __aenter__(self):
        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.request_timeout)
        )
        return self

    async def __aexit__(self, *_):
        if self.http_session:
            await self.http_session.close()

    async def collect_seed_data(self) -> List[SeedData]:
        seed_data_list = []

        async with AsyncSessionLocal() as db:
            territories = await self.territory_repo.get_all(db)

        for territory in territories:
            mock_seed_data = (
                [{"territory_id": territory.id, "name": "Пшеница", "price": 15000,
                  "date": datetime.now(timezone.utc) - timedelta(days=i)} for i in range(30)]
                + [{"territory_id": territory.id, "name": "Кукуруза", "price": 18000,
                    "date": datetime.now(timezone.utc) - timedelta(days=i)} for i in range(30)]
                + [{"territory_id": territory.id, "name": "Соя", "price": 22000,
                    "date": datetime.now(timezone.utc) - timedelta(days=i)} for i in range(30)]
            )
            for item in mock_seed_data:
                seed_data_list.append(SeedData(
                    territory_id=item["territory_id"],
                    name=item["name"],
                    price=item["price"],
                    date=item["date"],
                ))

        return seed_data_list

    async def collect_news_data(self) -> List[News]:
        news_list = []
        try:
            mock_news_data = [
                {
                    "title": "Новые технологии в сельском хозяйстве",
                    "content": "Исследования показывают, что новые технологии могут увеличить урожайность на 20%",
                    "date": datetime.now(timezone.utc) - timedelta(hours=i),
                }
                for i in range(24)
            ]

            async with AsyncSessionLocal() as db:
                territories = await self.territory_repo.get_all(db)

            for territory in territories:
                for item in mock_news_data:
                    news_list.append(News(
                        territory_id=territory.id,
                        title=item["title"],
                        content=item["content"],
                        date=item["date"],
                    ))
        except Exception as e:
            print(f"Error collecting news: {e}")

        return news_list

    async def save_seed_data(self, seed_data_list: List[SeedData]) -> None:
        if not seed_data_list:
            return
        async with AsyncSessionLocal() as db:
            await self.seed_data_repo.create_seed_data_batch(db, seed_data_list)

    async def save_news_data(self, news_list: List[News]) -> None:
        if not news_list:
            return
        async with AsyncSessionLocal() as db:
            await self.news_repo.create_news_batch(db, news_list)

    async def collect_and_store_all(self) -> Dict[str, Any]:
        result = {
            "seed_data_count": 0,
            "news_count": 0,
            "timestamp": datetime.now(timezone.utc),
        }

        seed_data = await self.collect_seed_data()
        await self.save_seed_data(seed_data)
        result["seed_data_count"] = len(seed_data)

        news_data = await self.collect_news_data()
        await self.save_news_data(news_data)
        result["news_count"] = len(news_data)

        return result