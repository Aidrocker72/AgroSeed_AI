# Многоступенчатая сборка для агрегации всех сервисов

# Базовый образ для Python-сервисов
FROM python:3.11-slim AS python-base
WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*


# Слой для установки зависимостей backend-api
FROM python-base AS backend-deps
COPY backend-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Слой для установки зависимостей etl-service
FROM python-base AS etl-deps
COPY etl-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Слой для установки зависимостей ai-service
FROM python-base AS ai-deps
COPY ai-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Сборка backend-api
FROM python-base AS backend-build
COPY --from=backend-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY backend-api/ .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# Сборка etl-service
FROM python-base AS etl-build
COPY --from=etl-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY etl-service/ .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# Сборка ai-service
FROM python-base AS ai-build
COPY --from=ai-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY ai-service/ .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# Сборка frontend
FROM node:18-alpine AS frontend-base
WORKDIR /app
COPY frontend/package.json .
RUN npm install


# Сборка frontend
FROM frontend-base AS frontend-build
COPY frontend/ .
RUN npm run build


# Финальный образ для запуска frontend
FROM node:18-alpine AS frontend-prod
WORKDIR /app
COPY --from=frontend-build /app/.output ./.output
COPY --from=frontend-build /app/package.json ./package.json
RUN npm install --production
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]