# Система «Умная премия»

> Внутренняя система для еженедельного взаимного голосования сотрудников с автоматическим расчётом премий (Django + Telegram Bot, без Telegram WebApp)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![SQLite](https://img.shields.io/badge/DB-SQLite-003B57.svg)](https://www.sqlite.org/index.html)
[![Django](https://img.shields.io/badge/Django-4.2-092E20.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-26A5E4.svg)](https://core.telegram.org/bots)

## 📋 Описание

«Умная премия» позволяет сотрудникам еженедельно оценивать коллег по шкале 0–10 в Telegram-боте. По завершении сессии система рассчитывает рейтинги и итоговые премии. Проект работает локально в вашей сети (без доменов), использует SQLite по умолчанию и не требует Telegram WebApp.

Ключевые особенности:
- 🗳️ Голосование через Telegram-бота (команды /start, /vote, /results)
- 💾 База данных по умолчанию — SQLite (файл db.sqlite3)
- 🌐 Работа по локальному IP (LAN), без публичного домена
- 🔐 Авторизация через Telegram (ID пользователя), без WebApp initData
- 📈 Результаты и отчётность в админке Django

## 🏗️ Архитектура

- Backend: Django 4.2 (DRF опционально)
- База данных: SQLite (по умолчанию). Возможен переход на PostgreSQL позже
- Очереди/планировщик: Celery (опционально), Redis не обязателен для локального старта
- Бот: python-telegram-bot (polling или webhook на локальный IP)

## 📚 Документация (wiki)

- [Описание проекта](wiki/00_project_description.md)
- [Архитектура](wiki/01_system_architectur.md)
- [Функциональные требования](wiki/02_functional_requirements.md)
- [API и интеграции](wiki/03_API_and_intengration.md)
- [Интерфейсы и UX](wiki/04_interface_and_UX.md)
- [База данных](wiki/05_database.md)
- [Администрирование](wiki/06_administration.md)
- [Тестирование](wiki/07_testing.md)

## 🚀 Быстрый старт (локальная сеть)

### 1) Клонировать и переключиться на ветку
```bash
git clone https://github.com/teristit/voting.git
cd voting
git checkout feature/smart-award-implementation
```

### 2) Установить зависимости backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3) Настройки окружения (.env)
Создайте файл backend/.env (минимум):
```
DEBUG=true
SECRET_KEY=dev-secret
ALLOWED_HOSTS=127.0.0.1,localhost,192.168.0.0/16
# Telegram Bot
TELEGRAM_BOT_TOKEN=123456:ABCDEF_your_token
```
Примечания:
- Telegram WebApp НЕ используется, переменные для WebApp можно не задавать
- Работать будем по локальному IP вашей машины (например, 192.168.1.15)

### 4) Инициализация БД (SQLite)
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5) Запуск Django (по локальному IP)
```bash
# пример: слушать на 0.0.0.0:8000, доступно в вашей LAN по IP хоста
python manage.py runserver 0.0.0.0:8000
```
Зайдите в админку: http://<ваш_LAN_IP>:8000/admin/

### 6) Запуск Telegram-бота (polling)
Рекомендуется polling-режим, чтобы не настраивать вебхуки и HTTPS.
```bash
python -m apps.telegram_bot.run_polling
```
Где apps/telegram_bot/run_polling.py должен вызывать Application.run_polling(). Мы добавим файл при необходимости.

Если хотите вебхук на локальный IP без домена — вам понадобится проброс порта/HTTPS (обычно не требуется для LAN). Polling проще.

## 🔧 Конфигурация

- БД по умолчанию — SQLite (backend/db.sqlite3). Меняется в backend/smart_award/settings.py
- Разрешённые хосты: укажите IP вашей машины в LAN в ALLOWED_HOSTS
- Бот: используйте polling. Для webhook потребуется внешний доступ и TLS — не рекомендуется в вашей конфигурации

## 📦 Структура (важные части)
```
backend/
  manage.py
  smart_award/
    settings.py
    urls.py
    wsgi.py
    celery.py (опционально)
  apps/
    telegram_bot/
      bot.py
    users/
      models.py
wiki/
  00_project_description.md
  01_system_architectur.md
  ...
```

## 🧪 Тестирование (минимум)
```bash
pytest -q  # если используете pytest/pytest-django
```

## 📄 Лицензия

MIT — как в текущем README.

---

Примечания по локальной работе:
- Используйте IP хоста в вашей сети (например, 192.168.1.15) для доступа к админке и API
- Polling для бота не требует домена/сертификата и работает из коробки
- SQLite хранит файл БД рядом с кодом; для резервного копирования — копируйте файл db.sqlite3