from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import asyncio
from services.data_collector import DataCollectorService
from config.settings import settings


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.data_collector = DataCollectorService()

    async def start(self):
        """
        Запуск планировщика задач
        """
        if settings.scheduler_enabled:
            # Добавляем задачи в планировщик
            self.scheduler.add_job(
                self._collect_seed_data_job,
                CronTrigger.from_crontab(settings.seeds_collection_interval),
                id='collect_seeds',
                name='Collect seed data'
            )
            
            self.scheduler.add_job(
                self._collect_news_job,
                CronTrigger.from_crontab(settings.news_collection_interval),
                id='collect_news',
                name='Collect news data'
            )
            
            self.scheduler.start()
            print(f"Scheduler started at {datetime.now()}")

    async def stop(self):
        """
        Остановка планировщика задач
        """
        self.scheduler.shutdown()
        print(f"Scheduler stopped at {datetime.now()}")

    async def _collect_seed_data_job(self):
        """
        Задача для сбора данных о семенах
        """
        print(f"Starting seed data collection job at {datetime.now()}")
        try:
            async with self.data_collector as collector:
                result = await collector.collect_and_store_all()
            print(f"Seed data collection completed: {result}")
        except Exception as e:
            print(f"Error in seed data collection job: {e}")

    async def _collect_news_job(self):
        """
        Задача для сбора новостей
        """
        print(f"Starting news collection job at {datetime.now()}")
        try:
            async with self.data_collector as collector:
                # В реальной реализации можно добавить отдельный метод для сбора только новостей
                result = await collector.collect_and_store_all()
            print(f"News collection completed: {result}")
        except Exception as e:
            print(f"Error in news collection job: {e}")

    async def run_once_seed_collection(self):
        """
        Метод для однократного запуска сбора данных о семенах
        """
        print(f"Running one-time seed data collection at {datetime.now()}")
        try:
            async with self.data_collector as collector:
                result = await collector.collect_and_store_all()
            print(f"One-time seed data collection completed: {result}")
            return result
        except Exception as e:
            print(f"Error in one-time seed data collection: {e}")
            raise

    async def run_once_news_collection(self):
        """
        Метод для однократного запуска сбора новостей
        """
        print(f"Running one-time news collection at {datetime.now()}")
        try:
            async with self.data_collector as collector:
                result = await collector.collect_and_store_all()
            print(f"One-time news collection completed: {result}")
            return result
        except Exception as e:
            print(f"Error in one-time news collection: {e}")
            raise