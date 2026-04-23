# Инструкция по запуску AgroSeed AI

## Требования

- Docker (v20.10 или выше)
- Docker Compose (v2.0 или выше)
- Git
- Python 3.11+ (для локальной разработки)
- Node.js 18+ (для локальной разработки frontend)

## Подготовка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/agroseed-ai.git
cd agroseed-ai
```

2. Убедитесь, что Docker и Docker Compose установлены:
```bash
docker --version
docker-compose --version
```

## Dev-режим (локальная разработка)

### Запуск всех сервисов

1. Установите переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

2. Запустите все сервисы с помощью Docker Compose:
```bash
docker-compose up --build
```

Альтернативно, можно запускать сервисы по отдельности:

### Запуск Backend API

```bash
cd backend-api
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Запуск ETL сервиса

```bash
cd etl-service
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Запуск AI сервиса

```bash
cd ai-service
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

### Запуск Frontend

```bash
cd frontend
npm install
npm run dev
```

### Запуск PostgreSQL

```bash
docker run --name agroseed-postgres \
  -e POSTGRES_DB=agroseed \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15
```

## Prod-режим (боевое развертывание)

### С использованием Docker Compose

1. Подготовьте файл `.env` с боевыми настройками:
```bash
# .env
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/agroseed
ETL_SERVICE_URL=http://etl-service:8000
AI_SERVICE_URL=http://ai-service:8000
```

2. Запустите сервисы в продакшен режиме:
```bash
docker-compose -f docker-compose.yml up -d --scale backend-api=2 --scale ai-service=2
```

### Масштабирование сервисов

Для увеличения количества экземпляров сервисов:
```bash
docker-compose up -d --scale backend-api=3 --scale etl-service=2
```

### Запуск с SSL/TLS

Для безопасного соединения рекомендуется использовать nginx-proxy:
```bash
# Запуск nginx-proxy с Let's Encrypt
docker network create proxy
docker run -d -p 80:80 -p 443:443 \
  --name nginx-proxy \
  --net proxy \
  -v /var/run/docker.sock:/tmp/docker.sock:ro \
  jwilder/nginx-proxy

# Запуск сервисов с настройками для HTTPS
docker-compose -f docker-compose.yml up -d
```

## Миграции базы данных

### Применение миграций

Для каждого сервиса выполните:
```bash
# Для backend-api
cd backend-api
alembic upgrade head

# Для etl-service
cd etl-service
alembic upgrade head
```

### Создание новых миграций

```bash
# В директории соответствующего сервиса
alembic revision --autogenerate -m "Описание миграции"
alembic upgrade head
```

## Тестирование

### Запуск unit-тестов

```bash
# Для backend-api
cd backend-api
python -m pytest tests/ -v

# Для etl-service
cd etl-service
python -m pytest tests/ -v

# Для ai-service
cd ai-service
python -m pytest tests/ -v
```

### Запуск интеграционных тестов

```bash
# После запуска всех сервисов
python -m pytest tests/integration/ -v
```

## Мониторинг и логирование

Сервисы выводят логи в stdout/stderr, которые можно посмотреть через Docker:
```bash
docker-compose logs -f backend-api
docker-compose logs -f etl-service
docker-compose logs -f ai-service
```

## Обновление сервисов

1. Обновите код:
```bash
git pull origin main
```

2. Пересоберите и запустите обновленные сервисы:
```bash
docker-compose build
docker-compose up -d
```

## Резервное копирование

Для создания резервной копии базы данных:
```bash
docker exec agroseed_postgres pg_dump -U user agroseed > backup_$(date +%Y%m%d_%H%M%S).sql
```

Для восстановления из резервной копии:
```bash
cat backup_file.sql | docker exec -i agroseed_postgres psql -U user agroseed