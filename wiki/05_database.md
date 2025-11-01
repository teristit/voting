# База данных (обновлено — дополнение)

Добавляется таблица OneTimeLogin:
- id (PK)
- code (uniq, varchar, индекс)
- telegram_id (bigint)
- expires_at (timestamp)
- used (boolean)
- created_at (timestamp)

Индексы по code, telegram_id, expires_at.
