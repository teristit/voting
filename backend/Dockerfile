FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения
COPY . .

# Создаем необходимые директории
RUN mkdir -p logs exports backups

# Открываем порт
EXPOSE 5000

# Устанавливаем переменные окружения
ENV FLASK_APP=app.py
ENV PYTHONPATH=/app

# Запускаем приложение
CMD ["python", "app.py"]
