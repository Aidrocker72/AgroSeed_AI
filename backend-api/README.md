# AgroSeed AI - Backend API

Backend API сервис для системы прогнозирования изменения цен сельхоз-семян.

## Описание

Backend API - это основной API-шлюз системы AgroSeed AI. Сервис реализует аутентификацию, управление пользователями, территориями и запуск прогнозов, делегируя аналитические задачи в AI и ETL сервисы.

## Архитектура

Сервис построен по многослойной архитектуре:
- **Routers** - точки входа API
- **Services** - бизнес-логика
- **Repositories** - работа с базой данных
- **Models** - ORM модели
- **Schemas** - Pydantic схемы

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
docker build -t agroseed-backend-api .
docker run -p 8000:8000 agroseed-backend-api
```

## API Endpoints

### Authentication
- `POST /auth/register` - Регистрация пользователя
- `POST /auth/login` - Авторизация пользователя
- `POST /auth/refresh` - Обновление токена

### Territories
- `GET /territories` - Список территорий
- `GET /territories/{id}` - Получение конкретной территории

### Forecasts
- `POST /forecast/run` - Запуск прогноза
- `GET /forecast/list` - Список прогнозов пользователя
- `GET /forecast/{id}` - Получение детального прогноза

## Технологии

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT авторизация
- Docker