# Система "Умная Премия"

Система для еженедельного голосования сотрудников с распределением бонусов, интегрированная с Telegram Mini App.

## Обзор системы

### Архитектура

- **Frontend**: Vue.js 3 + Telegram WebApp SDK + TailwindCSS
- **Backend**: Python 3.11 + Flask + SQLAlchemy
- **База данных**: PostgreSQL 15 (продакшн) / SQLite (разработка)
- **Кэш**: Redis
- **Очереди**: Celery + Redis

### Основные возможности

- 🗳️ **Голосование**: Оценка сотрудников по шкале 0-10
- 📊 **Аналитика**: Расчет результатов по алгоритму T1-T4
- 💰 **Бонусы**: Автоматическое распределение недельного бонуса
- 📁 **Экспорт**: Отчеты в Excel/CSV для бухгалтерии
- 🔐 **Безопасность**: Аутентификация через Telegram
- 🔧 **Администрирование**: Полный контроль сессий и пользователей

## Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Или локальная установка: Python 3.11+, Node.js 18+, PostgreSQL 15+

### Запуск через Docker Compose (рекомендуемо)

1. **Клонирование репозитория:**
```bash
git clone https://github.com/teristit/voting.git
cd voting
```

2. **Настройка окружения:**
```bash
cp .env.example .env
# Отредактируйте .env файл
```

3. **Запуск всех сервисов:**
```bash
docker-compose up -d
```

4. **Инициализация базы данных:**
```bash
docker-compose exec backend flask db upgrade
docker-compose exec backend python -c "from app import create_app; from models import *; app = create_app(); app.app_context().push(); db.create_all()"
```

### Локальная разработка

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt

# Настройка переменных окружения
export FLASK_ENV=development
export DATABASE_URL=sqlite:///smart_bonus.db  # для разработки

# Запуск
python app.py
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Конфигурация

### Основные переменные окружения

```env
# Общие настройки
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# База данных
DATABASE_URL=postgresql://user:password@localhost:5432/smart_bonus

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
VITE_TELEGRAM_BOT_USERNAME=your_bot_username

# Redis и Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# CORS
CORS_ORIGINS=https://your-domain.com
```

### Настройка Telegram Bot

1. Создайте бота через [@BotFather](https://t.me/botfather)
2. Получите токен и укажите в `TELEGRAM_BOT_TOKEN`
3. Настройте Web App через BotFather:
   - `/newapp`
   - Выберите бота
   - Укажите URL вашего frontendа

## API документация

### Основные эндпоинты

- `POST /api/v1/auth/telegram` - Аутентификация
- `GET /api/v1/sessions/current` - Текущая сессия
- `POST /api/v1/votes` - Отправка голосов
- `GET /api/v1/results/me` - Мои результаты
- `GET /api/v1/results/session/{id}` - Результаты сессии

Полная документация API находится в папке `docs/`.

## Администрирование

### Создание первого администратора

```bash
# Через Docker
docker-compose exec backend python -c "
from app import create_app
from models.user import User
from extensions import db
app = create_app()
with app.app_context():
    admin = User(
        name='Администратор',
        telegram_id=YOUR_TELEGRAM_ID,
        telegram_username='your_username',
        role='admin',
        active=True
    )
    db.session.add(admin)
    db.session.commit()
    print(f'Admin created: {admin.user_id}')
"

# Локально
python -c "...тот же код..."
```

### Основные команды

```bash
# Просмотр логов
docker-compose logs -f backend

# Создание резервной копии
docker-compose exec db pg_dump -U smart_bonus_user smart_bonus > backup.sql

# Восстановление из резервной копии
docker-compose exec -i db psql -U smart_bonus_user smart_bonus < backup.sql

# Обновление системы
git pull
docker-compose build
docker-compose up -d
```

## Продакшн развертывание

### SSL/HTTPS

Для продакшна рекомендуется использовать Nginx с SSL:

```bash
# Запуск с Nginx
docker-compose --profile production up -d
```

### Мониторинг

- Логи приложения: `docker-compose logs`
- Метрики PostgreSQL: `pg_stat_activity`
- Метрики Redis: `redis-cli info`

## Разработка

### Структура проекта

```
voting/
├── backend/                 # Flask API
│   ├── models/              # Модели данных
│   ├── routes/              # API маршруты
│   ├── services/            # Бизнес-логика
│   ├── utils/               # Утилиты
│   └── tests/               # Тесты
├── frontend/                # Vue.js приложение
│   ├── src/
│   │   ├── components/      # Vue компоненты
│   │   ├── views/           # Страницы
│   │   └── services/        # API клиенты
│   └── public/
├── docs/                    # Документация
├── docker-compose.yml       # Docker конфигурация
└── README.md
```

### Тестирование

```bash
# Backend тесты
cd backend
pytest

# Frontend тесты
cd frontend
npm run test
```

### Контрибьютинг

1. Создайте ветку для ваших изменений
2. Запустите тесты
3. Создайте Pull Request

## Поддержка

- **Документация**: [docs/](./docs/)
- **Issues**: [GitHub Issues](https://github.com/teristit/voting/issues)
- **Контакты**: dimitri.alexandr5w@yandex.ru

## Лицензия

MIT License - см. [LICENSE](LICENSE)
