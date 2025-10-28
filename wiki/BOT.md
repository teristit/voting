# BOT (обновлено)

- Режим: long polling (без публичного домена)
- Команды: /start, /vote, /results, /me, /admin
- Кнопка «Открыть веб‑панель»: вызывает `/auth/generate-code` → отправляет ссылку `http://LAN_IP:5173/login?code=...`
- Авторизация запроса к `/auth/generate-code` по X-API-Key
- Rate‑limit генерации кодов на telegram_id
