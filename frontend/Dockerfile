FROM node:18-alpine as build-stage

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY package*.json ./

# Устанавливаем зависимости
RUN npm ci --only=production

# Копируем все файлы проекта
COPY . .

# Собираем приложение для продакшена
RUN npm run build

# Production stage
FROM nginx:alpine as production-stage

# Копируем собранное приложение
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Копируем конфигурацию nginx (если есть)
# COPY nginx.conf /etc/nginx/nginx.conf

# Создаем простую конфигурацию nginx для SPA
RUN echo 'server {\n\
    listen 80;\n\
    server_name localhost;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    \n\
    # Обслуживание статических файлов\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    \n\
    # Кэширование статических ресурсов\n\
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {\n\
        expires 1y;\n\
        add_header Cache-Control "public, immutable";\n\
    }\n\
}' > /etc/nginx/conf.d/default.conf

# Открываем порт
EXPOSE 80

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"]