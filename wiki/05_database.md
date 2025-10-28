# Документация базы данных (без изменений для Bot)

Схема БД остаётся прежней. В контексте Telegram Bot меняются только источники аутентификации (по telegram_id) и логирование действий бота.

Дополнения:
- В `users` гарантировать индексы по `telegram_id`, `telegram_username`
- В `audit` добавлять `source: 'bot'|'web'`, `command` (для бота), `meta` с данными шага

См. основные таблицы: users, sessions, sessionparticipants, bonusparameters, votes, results, authsession, revokedtokens, auditlog, systemsettings.
