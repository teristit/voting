# Архитектура системы (обновлено)

## Каналы
- Telegram Bot → выдаёт одноразовые коды/ссылки для входа
- Веб (LAN): frontend (Vite+Vue) + backend (Flask+SQLite)

## Аутентификация
- Одноразовый код через бота → `/login?code=...` → `POST /auth/code-login` → JWT

## Компоненты
- Backend (Flask) слушает 0.0.0.0:5000 (LAN)
- Frontend (Vite) слушает 0.0.0.0:5173 (LAN)
- DB: SQLite в разработке (smart_bonus.db)
- Позже: PostgreSQL 17, Redis, Celery, Docker
