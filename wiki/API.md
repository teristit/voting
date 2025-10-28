# Backend API под Telegram‑бот + Web (LAN)

## Аутентификация
- POST /api/v1/auth/generate-code
  - Headers: X-API-Key: <BOT_BACKEND_KEY>
  - Body: { telegram_id: number }
  - Resp: { status: 'success', code: 'ABC123', expires_in: 600 }

- POST /api/v1/auth/code-login
  - Body: { code: 'ABC123' }
  - Resp: { status: 'success', token: '<jwt>', user: {...}, expires_in: 3600 }

- POST /api/v1/auth/logout (JWT)
- POST /api/v1/auth/refresh (JWT)

## Сессии/голосование (user)
- GET  /api/v1/sessions/current
- GET  /api/v1/sessions/{id}/participants
- POST /api/v1/votes { session_id, votes: [{target_id, score, comment?}] }
- GET  /api/v1/results/me
- GET  /api/v1/results/session/{id}

## Администрирование (admin)
- POST /api/v1/admin/sessions {start_date, end_date, autoparticipants?}
- POST /api/v1/admin/sessions/{id}/close
- POST /api/v1/admin/sessions/{id}/reopen
- GET  /api/v1/admin/sessions/{id}/votes
- PATCH /api/v1/admin/votes/{vote_id} {score?, comment?, modified_by_admin:true}
- DELETE /api/v1/admin/votes/{vote_id}
- GET  /api/v1/sessions/{id}/bonus-params
- POST /api/v1/sessions/{id}/bonus-params {average_weekly_revenue, participation_multiplier, total_weekly_bonus, participants_info}
- Экспорт: GET /api/v1/admin/export/session/{id}/results?format=xlsx|csv (blob)
          GET /api/v1/admin/export/session/{id}/participants?format=xlsx|csv (blob)
          GET /api/v1/admin/export/session/{id}/payments?format=csv (blob)
- Системные настройки: GET/PUT /api/v1/admin/settings

## Примечания по реализации
- OneTimeLogin(code, telegram_id, expires_at, used)
- TTL кода: 5–10 мин, rate-limit по telegram_id
- X-API-Key хранится на стороне бота и проверяется на backend
- Все изменения логируются в audit
