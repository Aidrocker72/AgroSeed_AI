# AgroSeed AI - ETL Service

ETL (Extract, Transform, Load) сервис для системы прогнозирования изменения цен сельхоз-семян.

## Описание

ETL сервис отвечает за сбор данных о ценах на семена и новостях из внешних источников, их обработку и загрузку в базу данных для дальнейшего анализа и прогнозирования.

## Архитектура

Сервис построен по многослойной архитектуре:
- **Routers** - точки входа API
- **Services** - бизнес-логика (сбор данных, планировщик)
- **Repositories** - работа с базой данных
- **Models** - ORM модели

## Функциональность

- Сбор данных о ценах на семена из внешних API
- Сбор новостей из RSS-лент
- Планировщик для периодического выполнения задач
- Загрузка данных в базу данных

## Запуск

### Локальный запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите приложение:
```bash
uvicorn main:app --reload
```

### Запуск в Docker

```bash
docker build -t agroseed-etl-service .
docker run -p 8000:8000 agroseed-etl-service
```

## API Endpoints

- `GET /etl/run/seeds` - Ручной запуск сбора данных о семенах
- `GET /etl/run/news` - Ручной запуск сбора новостей
- `GET /etl/status` - Статус планировщика задач

## Технологии

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- APScheduler
- aiohttp
- feedparser
- Docker