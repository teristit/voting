# API и интеграции (обновлено)

## Аутентификация
- `POST /api/v1/auth/generate-code` (только для бота, по X-API-Key): создать одноразовый код для telegram_id
- `POST /api/v1/auth/code-login` (пользователь по коду получает JWT)

## Telegram Bot
- Команды: /start, /help, /vote, /results, /me, /admin
- Inline‑кнопка «Открыть веб‑панель» → бот генерирует код и присылает ссылку `http://LAN_IP:5173/login?code=...`

## Сессии/Голоса/Результаты (без изменений по смыслу)
- `GET /api/v1/sessions/current`
- `GET /api/v1/sessions/{id}/participants`
- `POST /api/v1/votes`
- `GET /api/v1/results/me`
- `GET /api/v1/results/session/{id}`
