import aiohttp
import random
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone, date
from typing import List, Dict, Any, Optional, Tuple
from config.settings import settings
from config.territories import TERRITORIES as TERRITORY_FACTORS
from database.connection import AsyncSessionLocal
from database.models import SeedData, News, ETLRun, ExchangeRate
from repositories.seed_data import SeedDataRepository
from repositories.news import NewsRepository
from repositories.territory import TerritoryRepository
from repositories.etl_run import ETLRunRepository
from repositories.exchange_rate import ExchangeRateRepository

CROP_INDICATORS = {
    "Пшеница":      "PWHEAT",
    "Кукуруза":     "PMAIZ",
    "Соя":          "PSOYB",
    "Подсолнечник": "PSUNFLWR",
    "Ячмень":       "PBARL",
}

BASE_PRICES_USD = {
    "Пшеница":      240,
    "Кукуруза":     210,
    "Соя":          400,
    "Подсолнечник": 900,
    "Ячмень":       220,
}


class DataCollectorService:
    def __init__(self):
        self.seed_data_repo     = SeedDataRepository()
        self.news_repo          = NewsRepository()
        self.territory_repo     = TerritoryRepository()
        self.etl_run_repo       = ETLRunRepository()
        self.exchange_rate_repo = ExchangeRateRepository()
        self.http_session       = None

    async def __aenter__(self):
        self.http_session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.request_timeout)
        )
        return self

    async def __aexit__(self, *_):
        if self.http_session:
            await self.http_session.close()

    # ------------------------------------------------------------------ #
    #  World Bank — цены на сырьё                                         #
    # ------------------------------------------------------------------ #

    async def _fetch_wb_prices(self, indicator: str) -> Optional[Dict[str, float]]:
        """Месячные цены WB (USD/т). Возвращает {date_str: usd}."""
        url = f"{settings.world_bank_api_url}/country/WLD/indicator/{indicator}"
        params = {"format": "json", "mrv": 600, "per_page": 600, "frequency": "M"}
        try:
            async with self.http_session.get(url, params=params) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json(content_type=None)
                if not data or len(data) < 2 or not data[1]:
                    return None
                return {
                    r["date"]: float(r["value"])
                    for r in data[1] if r.get("value") is not None
                }
        except Exception as e:
            print(f"WB API error for {indicator}: {e}")
            return None

    # ------------------------------------------------------------------ #
    #  WB — цена нефти Brent (USD/барр.)                                  #
    # ------------------------------------------------------------------ #

    async def fetch_oil_prices(self, days: int = 90) -> List[ExchangeRate]:
        """Ежедневные цены на нефть Brent из WB (форвард-заполнение месячных данных)."""
        monthly = await self._fetch_wb_prices("POILBRENT")
        if not monthly:
            return []
        today = date.today()
        cutoff = today - timedelta(days=days)
        records: List[ExchangeRate] = []
        for date_str, price_usd in sorted(monthly.items()):
            try:
                year, month = int(date_str[:4]), int(date_str[5:])
                first_day = date(year, month, 1)
                last_day = (
                    date(year + 1, 1, 1) - timedelta(days=1)
                    if month == 12
                    else date(year, month + 1, 1) - timedelta(days=1)
                )
            except (ValueError, IndexError):
                continue
            cur = first_day
            while cur <= min(last_day, today):
                if cur >= cutoff:
                    records.append(ExchangeRate(
                        currency="OIL_USD",
                        date=datetime(cur.year, cur.month, cur.day, 12, 0, 0, tzinfo=timezone.utc),
                        rate=round(price_usd, 4),
                    ))
                cur += timedelta(days=1)
        return records

    # ------------------------------------------------------------------ #
    #  ЦБ РФ — курс USD/RUB                                               #
    # ------------------------------------------------------------------ #

    async def fetch_cbr_rates(self, days: int = 90) -> List[ExchangeRate]:
        """Исторические курсы USD/RUB из ЦБ РФ за последние N дней."""
        today = date.today()
        date_from = today - timedelta(days=days)
        url = "https://www.cbr.ru/scripts/XML_dynamic.asp"
        params = {
            "date_req1": date_from.strftime("%d/%m/%Y"),
            "date_req2": today.strftime("%d/%m/%Y"),
            "VAL_NM_RQ": "R01235",  # USD
        }
        try:
            async with self.http_session.get(url, params=params) as resp:
                if resp.status != 200:
                    return []
                # ЦБ отдаёт Windows-1251
                text = await resp.text(encoding="windows-1251")
                root = ET.fromstring(text)
                rates = []
                for record in root.findall("Record"):
                    raw_date = record.get("Date")        # DD.MM.YYYY
                    raw_value = record.find("Value").text  # "89,6579"
                    if not raw_date or not raw_value:
                        continue
                    d, m, y = raw_date.split(".")
                    dt = datetime(int(y), int(m), int(d), 12, 0, 0, tzinfo=timezone.utc)
                    rate = float(raw_value.replace(",", "."))
                    rates.append(ExchangeRate(currency="USD", date=dt, rate=rate))
                return rates
        except Exception as e:
            print(f"CBR API error: {e}")
            return []

    # ------------------------------------------------------------------ #
    #  Генерация данных по ценам                                          #
    # ------------------------------------------------------------------ #

    def _wb_prices_to_daily(
        self,
        monthly_prices: Dict[str, float],
        territory_id: int,
        territory_name: str,
        crop_name: str,
    ) -> List[SeedData]:
        factor = TERRITORY_FACTORS.get(territory_name, 1.0)
        today = datetime.now(timezone.utc).date()
        records = []
        for date_str, price_usd in sorted(monthly_prices.items()):
            try:
                year, month = int(date_str[:4]), int(date_str[5:])
                first_day = date(year, month, 1)
                last_day = (
                    date(year + 1, 1, 1) - timedelta(days=1)
                    if month == 12
                    else date(year, month + 1, 1) - timedelta(days=1)
                )
            except (ValueError, IndexError):
                continue
            cur = first_day
            while cur <= min(last_day, today):
                noise = 1 + random.uniform(-0.015, 0.015)
                price_rub = price_usd * settings.usd_to_rub_rate * factor * noise
                records.append(SeedData(
                    territory_id=territory_id,
                    name=crop_name,
                    price=round(price_rub, 2),
                    date=datetime(cur.year, cur.month, cur.day, 12, 0, 0, tzinfo=timezone.utc),
                ))
                cur += timedelta(days=1)
        return records

    def _generate_mock_prices(
        self, territory_id: int, territory_name: str, crop_name: str, days: int = 90
    ) -> List[SeedData]:
        factor = TERRITORY_FACTORS.get(territory_name, 1.0)
        base_rub = BASE_PRICES_USD.get(crop_name, 250) * settings.usd_to_rub_rate * factor
        now = datetime.now(timezone.utc)
        records = []
        price = base_rub
        for i in range(days, 0, -1):
            price *= 1 + random.uniform(-0.008, 0.012)
            records.append(SeedData(
                territory_id=territory_id,
                name=crop_name,
                price=round(price, 2),
                date=now - timedelta(days=i),
            ))
        return records

    # ------------------------------------------------------------------ #
    #  Сбор и сохранение                                                  #
    # ------------------------------------------------------------------ #

    async def collect_seed_data(self) -> Tuple[List[SeedData], str]:
        async with AsyncSessionLocal() as db:
            territories = await self.territory_repo.get_all(db)
        seed_data_list: List[SeedData] = []
        source = "mock"
        for crop_name, indicator in CROP_INDICATORS.items():
            wb_prices = await self._fetch_wb_prices(indicator)
            if wb_prices:
                source = "world_bank"
                for t in territories:
                    seed_data_list.extend(
                        self._wb_prices_to_daily(wb_prices, t.id, t.name, crop_name)
                    )
            else:
                for t in territories:
                    seed_data_list.extend(
                        self._generate_mock_prices(t.id, t.name, crop_name)
                    )
        return seed_data_list, source

    async def collect_news_data(self) -> List[News]:
        news_list = []
        try:
            mock_news = [
                {
                    "title": "Новые технологии в сельском хозяйстве",
                    "content": "Исследования показывают, что новые технологии могут увеличить урожайность на 20%",
                    "date": datetime.now(timezone.utc) - timedelta(hours=i),
                }
                for i in range(24)
            ]
            async with AsyncSessionLocal() as db:
                territories = await self.territory_repo.get_all(db)
            for t in territories:
                for item in mock_news:
                    news_list.append(News(
                        territory_id=t.id,
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
        started_at = datetime.now(timezone.utc)
        async with AsyncSessionLocal() as db:
            etl_run = await self.etl_run_repo.create(
                db, ETLRun(started_at=started_at, status="running")
            )
            etl_run_id = etl_run.id

        result: Dict[str, Any] = {
            "seed_data_count": 0,
            "news_count": 0,
            "exchange_rates_count": 0,
            "timestamp": started_at.isoformat(),
            "data_source": "mock",
        }

        try:
            # Курс ЦБ РФ
            cbr_rates = await self.fetch_cbr_rates(days=90)
            if cbr_rates:
                async with AsyncSessionLocal() as db:
                    await self.exchange_rate_repo.upsert_batch(db, cbr_rates)
                result["exchange_rates_count"] = len(cbr_rates)

            # Цена нефти Brent
            oil_rates = await self.fetch_oil_prices(days=90)
            if oil_rates:
                async with AsyncSessionLocal() as db:
                    await self.exchange_rate_repo.upsert_batch(db, oil_rates)

            # Цены на семена
            seed_data, source = await self.collect_seed_data()
            await self.save_seed_data(seed_data)
            result["seed_data_count"] = len(seed_data)
            result["data_source"] = source

            # Новости
            news_data = await self.collect_news_data()
            await self.save_news_data(news_data)
            result["news_count"] = len(news_data)

            async with AsyncSessionLocal() as db:
                await self.etl_run_repo.update_run(
                    db, etl_run_id,
                    status="success",
                    completed_at=datetime.now(timezone.utc),
                    seed_data_count=result["seed_data_count"],
                    news_count=result["news_count"],
                    data_source=source,
                )
        except Exception as e:
            async with AsyncSessionLocal() as db:
                await self.etl_run_repo.update_run(
                    db, etl_run_id,
                    status="failed",
                    completed_at=datetime.now(timezone.utc),
                    error=str(e),
                )
            raise

        return result
