# ---- Стадия 1: Сборка приложения ----
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Объявляем аргумент сборки для URL API
ARG VITE_API_URL
# Устанавливаем его как переменную окружения для процесса сборки Vite
ENV VITE_API_URL=${VITE_API_URL}

# Используем правильную команду для производственной сборки
RUN npm run build

# ---- Стадия 2: Сервинг статических файлов с помощью Nginx ----
FROM nginx:1.25-alpine

# Копируем собранные статические файлы из папки /app/dist
COPY --from=builder /app/dist /usr/share/nginx/html

# Копируем кастомную конфигурацию Nginx (пример ниже)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]