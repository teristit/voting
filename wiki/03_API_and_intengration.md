# API и интеграции (актуализировано: Bot + Web LAN)

## Аутентификация
- `POST /api/v1/auth/generate-code`
  - Авторизация: заголовок `X-API-Key: <BOT_BACKEND_KEY>`
  - Тело: `{ "telegram_id": <int> }`
  - Ответ: `{ "status":"success", "code":"<ONE_TIME_CODE>", "expires_at":"<ISO>" }`
- `POST /api/v1/auth/code-login`
  - Тело: `{ "code": "<ONE_TIME_CODE>" }`
  - Ответ: `{ "status":"success", "token":"<JWT>", "user": { ... }, "expires_in": <sec> }`

## Сессии/Голоса/Результаты
- `GET /api/v1/sessions/current`
- `GET /api/v1/sessions/{id}/participants`
- `POST /api/v1/votes`
- `GET /api/v1/results/me`
- `GET /api/v1/results/session/{id}`

Примечания: коды одноразовые (TTL 5–10 минут), аудит входов, rate‑limit на генерацию.
