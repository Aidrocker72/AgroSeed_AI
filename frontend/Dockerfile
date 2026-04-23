# Многоступенчатая сборка для оптимизации
# Stage 1: Сборка приложения
FROM node:18-alpine AS builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальные файлы проекта
COPY . .

# Собираем приложение
RUN npm run build

# Stage 2: Запуск приложения
FROM node:18-alpine AS production

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости только для продакшена
COPY package*.json ./
RUN npm install --only=production

# Копируем скомпилированные файлы из stage 1
COPY --from=builder /app/.output ./.output

# Открываем порт
EXPOSE 3000

# Запускаем приложение
CMD ["node", ".output/server/index.mjs"]