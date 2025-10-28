# FRONTEND (обновлено)

- Маршрут /login: чтение ?code и вызов /auth/code-login
- Auth store: loginByCode(code)
- Конфиг LAN: `VITE_API_BASE_URL=http://LAN_IP:5000/api/v1`, запуск `npm run dev -- --host`
- Убрать зависимость от Telegram.WebApp.initData
