# Wiki: Система «Умная Премия» — Телеграм-бот + Веб (LAN)

Этот wiki отражает актуальную концепцию:
- Взаимодействие в Telegram осуществляется через **бота** (не Mini App)
- **Веб-интерфейс** остаётся и работает в локальной сети для голосования и администрирования
- На текущем этапе **без Docker, Redis, PostgreSQL** — используется **Flask + SQLite**

Содержание
1. Обзор архитектуры
2. Развёртывание в локальной сети
3. Аутентификация через одноразовый код от бота (Code Login)
4. Telegram-бот: команды и сценарии
5. Backend API (актуальные эндпоинты)
6. Frontend (страницы и переменные окружения)
7. Модель данных: дополнение (OneTimeLogin)
8. Безопасность и аудит
9. Планы на будущее (PostgreSQL 17, Redis, Docker)

---

## 1. Обзор архитектуры

- Telegram Bot: чат-команды, inline-кнопки, генерация одноразовых ссылок на веб.
- Web (SPA на Vue): голосование, результаты, админка. Доступна в LAN.
- Backend (Flask): API, аутентификация, расчёты T1→T4, экспорт CSV/XLSX, журнал аудита.
- DB: SQLite (smart_bonus.db в папке backend).

Трафик: 
- Пользователь ↔ Telegram ↔ Бот (long polling)
- Пользователь ↔ Web (http://LAN_IP:5173) ↔ Backend (http://LAN_IP:5000)

## 2. Развёртывание в локальной сети

1) Узнайте IP машины (LAN_IP), например 192.168.1.50
2) Backend:
- .env в корне: DB_FILE=smart_bonus.db, DEBUG=True, CORS_ORIGINS=*
- cd backend; python -m venv venv; activate; pip install -r requirements.txt; python app.py
- Доступ: http://LAN_IP:5000
3) Frontend:
- frontend/.env: VITE_API_BASE_URL=http://LAN_IP:5000/api/v1
- cd frontend; npm install; npm run dev -- --host
- Доступ: http://LAN_IP:5173

## 3. Аутентификация через одноразовый код от бота (Code Login)

Поток:
1) Пользователь пишет боту → кнопка «Открыть веб‑панель»
2) Бот вызывает `POST /api/v1/auth/generate-code` (по X-API-Key), получает одноразовый CODE
3) Бот отправляет ссылку: `http://LAN_IP:5173/login?code=CODE`
4) Фронт на /login читает `code`, вызывает `POST /api/v1/auth/code-login`
5) Backend валидирует код (не просрочен, не использован), помечает used=true, выдаёт JWT + user
6) Фронт сохраняет токен и переводит в приложение

Параметры кодов:
- TTL: 5–10 минут
- Одноразовые, связаны с telegram_id
- Rate-limit генерации для каждого telegram_id

## 4. Telegram-бот: команды и сценарии

Команды:
- /start — регистрация/привязка telegram_id, меню
- /vote — краткое состояние голосования + кнопка «Открыть веб‑панель»
- /results — мои результаты + кнопка «Открыть веб‑панель»
- /me — профиль и подсказки
- /admin — меню админа (если роль=admin): быстрые ссылки на админку

Inline‑кнопки:
- «Открыть веб‑панель» → сгенерировать code → отправить ссылку с ?code=...

Технически бот работает по long polling — публичный домен не нужен.

## 5. Backend API (актуальные эндпоинты)

Аутентификация:
- POST /api/v1/auth/generate-code  (X-API-Key, body: telegram_id)
- POST /api/v1/auth/code-login     (body: code)
- POST /api/v1/auth/logout         (JWT)
- POST /api/v1/auth/refresh        (JWT refresh)

Сессии и голосование (пользователь):
- GET  /api/v1/sessions/current
- GET  /api/v1/sessions/{id}/participants
- POST /api/v1/votes                   (body: session_id, votes[])
- GET  /api/v1/results/me
- GET  /api/v1/results/session/{id}

Администрирование:
- POST /api/v1/admin/sessions
- POST /api/v1/admin/sessions/{id}/close
- POST /api/v1/admin/sessions/{id}/reopen
- GET  /api/v1/admin/sessions/{id}/votes
- PATCH/DELETE /api/v1/admin/votes/{vote_id}
- GET/POST /api/v1/sessions/{id}/bonus-params
- Экспорт: /api/v1/admin/export/session/{id}/(results|participants|payments)?format=xlsx|csv
- Системные настройки: /api/v1/admin/settings (GET/PUT)

(Пути могут уточняться по мере реализации; фронт ориентируется на эти контракты.)

## 6. Frontend (страницы и переменные окружения)

Страницы:
- / — Главная (статус сессии, быстрые действия)
- /voting — Голосование 0–10
- /results — Результаты (топ-3, таблица)
- /history — История (будет дорабатываться)
- /profile — Профиль и настройки
- /admin — Админка (будет дорабатываться)
- /login — Вход по коду (читает ?code= и вызывает /auth/code-login)

Переменные окружения (frontend/.env):
- VITE_API_BASE_URL=http://LAN_IP:5000/api/v1
- VITE_TELEGRAM_BOT_USERNAME= (опционально)

## 7. Модель данных: дополнение (OneTimeLogin)

OneTimeLogin:
- id (PK)
- code (string, unique)
- telegram_id (bigint)
- expires_at (timestamp)
- used (boolean)
- created_at (timestamp)

Индексы: code (unique), telegram_id, expires_at

## 8. Безопасность и аудит
- Коды одноразовые, TTL ограничен
- Генерация кодов только с валидным X-API-Key (для бота)
- Логи аудита: вход по коду, генерация кода, действие админов
- CORS: для LAN можно оставить `*`, но рекомендуется сузить до IP фронтенда
- Фаерволл: открыты только 5000 (API) и 5173 (front) внутри LAN

## 9. Планы на будущее
- Перейти на PostgreSQL 17, добавить Alembic миграции
- Включить Redis + Celery для фоновых задач (рассылки, тяжёлые экспорты)
- Docker/Docker Compose для продакшн окружений
- Расширенная админка (bulk‑импорт, реальное‑время мониторинг)
- Полноценные уведомления через бота
