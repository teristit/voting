# Администрирование системы «Умная премия»

## Содержание
1. [Управление сотрудниками](#1-управление-сотрудниками)
2. [Управление сессиями голосования](#2-управление-сессиями-голосования)
3. [Управление участниками голосования](#3-управление-участниками-голосования)
4. [Параметры премии](#4-параметры-премии)
5. [Просмотр и экспорт результатов](#5-просмотр-и-экспорт-результатов)
6. [Управление голосами](#6-управление-голосами)
7. [Логирование и аудит](#7-логирование-и-аудит)
8. [Системные настройки](#8-системные-настройки)
9. [Чек-листы администратора](#9-чек-листы-администратора)

---

## 1. Управление сотрудниками

### 1.1 Добавление нового сотрудника

#### Через веб-интерфейс
1. Перейти в раздел **"Сотрудники"** → **"Управление сотрудниками"**
2. Нажать кнопку **"Добавить сотрудника"**
3. Заполнить форму:
   - **User ID** (Telegram ID) - обязательное поле
   - **ФИО** - полное имя сотрудника
   - **Telegram username** - опционально
   - **Email** - опционально
   - **Роль** - user/manager/admin
   - **Активность** - включено по умолчанию
4. Нажать **"Сохранить"**

#### Через API
```bash
POST /api/v1/admin/users
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "user_id": 105,
  "name": "Сергеев Алексей",
  "telegram_username": "alexey_sergeev",
  "email": "alexey@company.com",
  "role": "user",
  "active": true
}
```

**Ответ:**
```json
{
  "status": "success",
  "message": "Пользователь добавлен",
  "user": {
    "user_id": 105,
    "name": "Сергеев Алексей",
    "telegram_username": "alexey_sergeev",
    "role": "user",
    "active": true,
    "created_at": "2024-03-20T10:30:00"
  }
}
```

### 1.2 Массовое добавление сотрудников

#### Через CSV-импорт
1. Подготовить CSV файл в формате:
```csv
user_id,name,telegram_username,email,role,active
101,Иванов Иван,ivanov,ivan@company.com,user,true
102,Петров Петр,petrov,petr@company.com,manager,true
103,Сидорова Анна,sidorova,anna@company.com,user,true
```

2. В админ-панели: **"Сотрудники"** → **"Импорт из CSV"**
3. Загрузить файл и подтвердить импорт

#### Через API массового добавления
```bash
POST /api/v1/admin/users/bulk
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "users": [
    {
      "user_id": 101,
      "name": "Иванов Иван",
      "telegram_username": "ivanov",
      "role": "user",
      "active": true
    },
    {
      "user_id": 102, 
      "name": "Петров Петр",
      "telegram_username": "petrov",
      "role": "manager",
      "active": true
    }
  ]
}
```

### 1.3 Редактирование сотрудника

#### Через веб-интерфейс
1. Найти сотрудника в списке
2. Нажать **"Редактировать"**
3. Внести изменения
4. Сохранить

#### Через API
```bash
PUT /api/v1/admin/users/105
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "name": "Сергеев Алексей Николаевич",
  "email": "alexey.n@company.com",
  "role": "manager",
  "active": true
}
```

### 1.4 Исключение сотрудника

#### Временное отключение (деактивация)
```bash
POST /api/v1/admin/users/105/deactivate
Authorization: Bearer {admin_token}
```

**Последствия деактивации:**
- Сотрудник не может войти в систему
- Не отображается в списках для голосования
- Сохраняет историю прошлых голосований
- Можно восстановить в любой момент

#### Полное удаление (только через API)
```bash
DELETE /api/v1/admin/users/105
Authorization: Bearer {admin_token}
```

**Внимание:** Полное удаление безвозвратно удаляет все данные пользователя.

### 1.5 Восстановление сотрудника

```bash
POST /api/v1/admin/users/105/activate
Authorization: Bearer {admin_token}
```

### 1.6 Назначение ролей

#### Изменение роли сотрудника
```bash
PUT /api/v1/admin/users/105/role
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "role": "manager",
  "permissions": ["users:read", "results:read", "exports:read"]
}
```

**Доступные роли:**
- **user** - обычный сотрудник
- **manager** - руководитель с ограниченными правами
- **admin** - полный доступ ко всем функциям

---

## 2. Управление сессиями голосования

### 2.1 Создание новой сессии

#### Через веб-интерфейс
1. Перейти в раздел **"Сессии"** → **"Создать сессию"**
2. Задать параметры:
   - **Дата начала** (обычно суббота)
   - **Дата окончания** (обычно вторник)
   - **Автоматическая активация** (включить)
   - **Автоматическое добавление участников** (включить)
3. Нажать **"Создать"**

#### Через API
```bash
POST /api/v1/admin/sessions
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "start_date": "2024-10-21",
  "end_date": "2024-10-27",
  "active": true,
  "auto_participants": true
}
```

**Ответ:**
```json
{
  "status": "success",
  "session_id": 18,
  "message": "Сессия создана",
  "session": {
    "session_id": 18,
    "start_date": "2024-10-21",
    "end_date": "2024-10-27",
    "active": true,
    "auto_participants": true,
    "created_at": "2024-10-20T14:00:00"
  }
}
```

### 2.2 Автоматическое создание сессий

#### Настройка регулярного создания
```bash
PUT /api/v1/admin/settings
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "auto_create_sessions": true,
  "session_start_day": "monday",
  "session_duration_days": 7,
  "advance_creation_days": 1,
  "auto_add_participants": true
}
```

### 2.3 Просмотр активных сессий

```bash
GET /api/v1/admin/sessions/active
Authorization: Bearer {admin_token}
```

**Ответ:**
```json
{
  "sessions": [
    {
      "session_id": 18,
      "start_date": "2024-10-21",
      "end_date": "2024-10-27",
      "active": true,
      "created_at": "2024-10-20T14:00:00",
      "participants_stats": {
        "total_participants": 32,
        "can_vote": 28,
        "can_receive_votes": 30,
        "has_voted": 15,
        "participation_rate": 53.6
      }
    }
  ]
}
```

### 2.4 Закрытие сессии

#### Ручное закрытие
```bash
POST /api/v1/admin/sessions/18/close
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "forced": false,
  "calculate_results": true
}
```

**Параметры:**
- `forced` - true для принудительного закрытия, даже если не все проголосовали
- `calculate_results` - true для автоматического расчета результатов

**Ответ:**
```json
{
  "status": "success",
  "message": "Сессия закрыта",
  "session_id": 18,
  "results_summary": {
    "participants_count": 28,
    "votes_count": 756,
    "average_score": 7.65,
    "total_bonus_distributed": 37459.60
  }
}
```

### 2.5 Повторное открытие сессии

```bash
POST /api/v1/admin/sessions/18/reopen
Authorization: Bearer {admin_token}
```

**Условия повторного открытия:**
- Сессия была закрыта не более 72 часов назад
- Все голоса сохраняются
- Голосование продлевается на 24 часа

**Ответ:**
```json
{
  "status": "success",
  "message": "Сессия №18 повторно открыта",
  "new_end_date": "2024-10-28T23:59:59"
}
```

### 2.6 Просмотр истории сессий

```bash
GET /api/v1/admin/sessions?page=1&limit=20
Authorization: Bearer {admin_token}
```

---

## 3. Управление участниками голосования

### 3.1 Автоматическое управление участниками

#### При создании сессии с auto_participants = true
Система автоматически:
1. Получает всех активных пользователей
2. Создает записи в `session_participants`
3. Устанавливает:
   - `can_vote = true` для обычных пользователей
   - `can_vote = false` для администраторов (по умолчанию)
   - `can_receive_votes = true` для всех
   - `status = 'active'`

### 3.2 Ручное управление участниками

#### Добавление участников в сессию
```bash
POST /api/v1/admin/sessions/18/participants
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "user_ids": [101, 102, 103, 104],
  "can_vote": true,
  "can_receive_votes": true,
  "status": "active"
}
```

**Ответ:**
```json
{
  "status": "success",
  "message": "Участники добавлены в сессию",
  "added_count": 4,
  "failed_count": 0
}
```

#### Массовое добавление из списка активных пользователей
```bash
POST /api/v1/admin/sessions/18/participants/add-active
Authorization: Bearer {admin_token}
```

### 3.3 Просмотр списка участников

```bash
GET /api/v1/admin/sessions/18/participants
Authorization: Bearer {admin_token}
```

**Ответ:**
```json
{
  "session_id": 18,
  "participants": [
    {
      "participant_id": 1,
      "user_id": 101,
      "name": "Иванов Иван",
      "telegram_username": "ivanov",
      "can_vote": true,
      "can_receive_votes": true,
      "status": "active",
      "has_voted": false,
      "votes_received": 0
    },
    {
      "participant_id": 2,
      "user_id": 102,
      "name": "Петров Петр",
      "telegram_username": "petrov",
      "can_vote": true,
      "can_receive_votes": true,
      "status": "active", 
      "has_voted": true,
      "votes_received": 5
    },
    {
      "participant_id": 3,
      "user_id": 103,
      "name": "Сидорова Анна",
      "telegram_username": "sidorova",
      "can_vote": false,
      "can_receive_votes": true,
      "status": "vacation",
      "has_voted": false,
      "votes_received": 3
    }
  ],
  "summary": {
    "total_participants": 32,
    "can_vote": 28,
    "can_receive_votes": 30,
    "has_voted": 15,
    "participation_rate": 53.6
  }
}
```

### 3.4 Изменение прав участника

```bash
PATCH /api/v1/admin/sessions/18/participants/3
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "can_vote": false,
  "can_receive_votes": true,
  "status": "vacation",
  "reason": "Сотрудник в отпуске"
}
```

**Доступные статусы:**
- `active` - активный участник
- `excluded` - исключен из голосования
- `vacation` - в отпуске
- `sick_leave` - на больничном

### 3.5 Исключение участника из сессии

```bash
DELETE /api/v1/admin/sessions/18/participants/3
Authorization: Bearer {admin_token}
```

**Или через изменение статуса:**
```bash
PATCH /api/v1/admin/sessions/18/participants/3
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "can_vote": false,
  "can_receive_votes": false,
  "status": "excluded"
}
```

### 3.6 Массовые операции с участниками

#### Изменение статуса для нескольких участников
```bash
POST /api/v1/admin/sessions/18/participants/bulk-status
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "user_ids": [101, 102, 103],
  "can_vote": false,
  "status": "vacation",
  "reason": "Корпоративное мероприятие"
}
```

#### Импорт участников из CSV
```bash
POST /api/v1/admin/sessions/18/participants/import
Authorization: Bearer {admin_token}
Content-Type: multipart/form-data

file: {csv_file}
```

**Формат CSV:**
```csv
user_id,can_vote,can_receive_votes,status
101,true,true,active
102,false,true,vacation
103,true,false,sick_leave
```

---

## 4. Параметры премии

### 4.1 Установка параметров для сессии

#### Через веб-интерфейс
1. Перейти в **"Сессии"** → выбрать активную сессию → **"Параметры премии"**
2. Заполнить форму:
   - **Средняя недельная выручка**
   - **Множитель участия** (0-1)
   - **Общая сумма премии**
   - **Информация о составе команды**
3. Сохранить

#### Через API
```bash
POST /api/v1/admin/sessions/18/bonus-params
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "average_weekly_revenue": 3057926.67,
  "participation_multiplier": 0.875,
  "total_weekly_bonus": 37459.60,
  "participants_info": {
    "total_potential": 32,
    "refused": 4,
    "active": 28,
    "on_vacation": 2
  }
}
```

### 4.2 Шаблоны параметров

#### Создание шаблона
```bash
POST /api/v1/admin/bonus-templates
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "template_name": "Высокая выручка",
  "average_weekly_revenue": 3500000.00,
  "participation_multiplier": 0.9,
  "total_weekly_bonus": 45000.00
}
```

#### Применение шаблона
```bash
POST /api/v1/admin/sessions/18/apply-template/1
Authorization: Bearer {admin_token}
```

### 4.3 Просмотр текущих параметров

```bash
GET /api/v1/admin/sessions/18/bonus-params
Authorization: Bearer {admin_token}
```

---

## 5. Просмотр и экспорт результатов

### 5.1 Просмотр результатов в реальном времени

#### Статистика сессии
```bash
GET /api/v1/admin/sessions/18/stats
Authorization: Bearer {admin_token}
```

**Ответ:**
```json
{
  "session_id": 18,
  "status": "active",
  "total_participants": 32,
  "voted_participants": 28,
  "participation_rate": 87.5,
  "total_votes": 756,
  "average_score": 7.65,
  "votes_remaining": 4,
  "time_remaining": "2 days 5 hours"
}
```

#### Детальные результаты
```bash
GET /api/v1/admin/sessions/18/results
Authorization: Bearer {admin_token}
```

**Ответ:**
```json
{
  "session_id": 18,
  "status": "closed",
  "results": [
    {
      "user_id": 101,
      "name": "Иванов Иван",
      "average_score": 8.2,
      "rank": 1,
      "votes_received": 28,
      "total_bonus": 1845.25,
      "calculation_details": {
        "T2_score": 8.0,
        "T3_normalized": 8.5,
        "T4_final": 8.2
      }
    },
    {
      "user_id": 102,
      "name": "Петров Петр",
      "average_score": 7.8,
      "rank": 2,
      "votes_received": 27,
      "total_bonus": 1541.81
    }
  ],
  "summary": {
    "total_participants": 28,
    "total_bonus_distributed": 37459.60,
    "average_score": 7.65,
    "participation_rate": 87.5
  }
}
```

### 5.2 Экспорт результатов

#### Экспорт в XLSX (Excel)
```bash
GET /api/v1/admin/export/session/18?format=xlsx
Authorization: Bearer {admin_token}
```

**Содержимое файла:**
- Сводная таблица с результатами
- Детализация по голосам
- Промежуточные расчёты (_T1–_T4)
- Статистика сессии

#### Экспорт в CSV
```bash
GET /api/v1/admin/export/session/18?format=csv
Authorization: Bearer {admin_token}
```

#### Экспорт для бухгалтерии
```bash
GET /api/v1/admin/export/session/18/payments?format=csv
Authorization: Bearer {admin_token}
```

**Содержимое (упрощенный формат):**
```csv
ФИО,Премия,Реквизиты
Иванов Иван,1845.25,...
Петров Петр,1541.81,...
```

### 5.3 Сравнительная аналитика

#### Сравнение сессий
```bash
GET /api/v1/admin/analytics/sessions/comparison?session_ids=16,17,18
Authorization: Bearer {admin_token}
```

**Ответ:**
```json
{
  "comparison": [
    {
      "session_id": 16,
      "period": "2024-10-07 - 2024-10-13",
      "average_score": 7.45,
      "participation_rate": 85.2,
      "total_bonus": 35200.00,
      "total_participants": 31
    },
    {
      "session_id": 17,
      "period": "2024-10-14 - 2024-10-20", 
      "average_score": 7.58,
      "participation_rate": 88.1,
      "total_bonus": 36800.00,
      "total_participants": 32
    },
    {
      "session_id": 18,
      "period": "2024-10-21 - 2024-10-27",
      "average_score": 7.65,
      "participation_rate": 87.5,
      "total_bonus": 37459.60,
      "total_participants": 32
    }
  ],
  "trends": {
    "score_trend": "up",
    "participation_trend": "stable", 
    "bonus_trend": "up",
    "participants_trend": "stable"
  }
}
```

---

## 6. Управление голосами

### 6.1 Просмотр всех голосов сессии

```bash
GET /api/v1/admin/sessions/18/votes
Authorization: Bearer {admin_token}
```

**Ответ:**
```json
{
  "session_id": 18,
  "votes": [
    {
      "vote_id": 551,
      "voter_id": 101,
      "voter_name": "Иван Иванов",
      "target_id": 102,
      "target_name": "Петр Петров", 
      "score": 8,
      "modified_by_admin": false,
      "timestamp": "2024-10-21T12:31:00"
    },
    {
      "vote_id": 552,
      "voter_id": 103,
      "target_id": 104,
      "score": 7,
      "modified_by_admin": true,
      "timestamp": "2024-10-21T14:22:00"
    }
  ],
  "total_count": 756
}
```

### 6.2 Изменение оценки

```bash
PATCH /api/v1/admin/votes/551
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "new_score": 9,
  "reason": "Корректировка по просьбе сотрудника"
}
```

**Ответ:**
```json
{
  "status": "success",
  "message": "Оценка обновлена",
  "vote_id": 551,
  "old_score": 8,
  "new_score": 9,
  "recalculation_triggered": true
}
```

### 6.3 Удаление голоса

```bash
DELETE /api/v1/admin/votes/551
Authorization: Bearer {admin_token}
```

**Ответ:**
```json
{
  "status": "success", 
  "message": "Голос удалён",
  "vote_id": 551,
  "recalculation_triggered": true
}
```

### 6.4 Принудительный перерасчёт результатов

```bash
POST /api/v1/admin/sessions/18/recalculate
Authorization: Bearer {admin_token}
```

**Используется после:**
- Изменения голосов администратором
- Обновления параметров премии
- Исправления ошибок в расчетах

---

## 7. Логирование и аудит

### 7.1 Просмотр журнала действий

#### Весь журнал с фильтрацией
```bash
GET /api/v1/admin/logs?user_id=101&session_id=18&action=vote_submit&date_from=2024-10-21&page=1&limit=50
Authorization: Bearer {admin_token}
```

**Параметры фильтрации:**
- `user_id` - действия конкретного пользователя
- `session_id` - действия в рамках сессии
- `action` - тип действия
- `date_from`, `date_to` - временной диапазон
- `page`, `limit` - пагинация

**Ответ:**
```json
{
  "logs": [
    {
      "log_id": 1245,
      "timestamp": "2024-10-21T09:15:30",
      "user_id": 101,
      "user_name": "Иван Иванов",
      "action": "vote_submit",
      "details": {
        "session_id": 18,
        "votes_count": 5,
        "average_given_score": 7.4
      },
      "session_id": 18,
      "ip_address": "192.168.1.100",
      "user_agent": "Telegram WebApp"
    },
    {
      "log_id": 1246,
      "timestamp": "2024-10-21T10:20:15",
      "user_id": 1,
      "user_name": "Администратор",
      "action": "update_bonus_params",
      "details": {
        "session_id": 18,
        "changes": {
          "total_weekly_bonus": "35000.00 → 37459.60"
        }
      },
      "session_id": 18,
      "ip_address": "192.168.1.50",
      "user_agent": "Chrome/118.0.0.0"
    }
  ],
  "total_count": 245,
  "page": 1,
  "page_size": 50,
  "total_pages": 5
}
```

### 7.2 Типы логируемых действий

| Действие | Уровень | Описание |
|----------|---------|----------|
| `user_login` | INFO | Вход пользователя в систему |
| `user_logout` | INFO | Выход пользователя из системы |
| `vote_submit` | INFO | Отправка голосов |
| `vote_update` | WARN | Изменение отправленных голосов |
| `vote_delete` | WARN | Удаление голосов |
| `session_create` | INFO | Создание сессии |
| `session_close` | INFO | Закрытие сессии |
| `session_reopen` | WARN | Повторное открытие сессии |
| `user_create` | INFO | Добавление сотрудника |
| `user_update` | INFO | Редактирование сотрудника |
| `user_deactivate` | WARN | Деактивация сотрудника |
| `user_activate` | INFO | Активация сотрудника |
| `role_change` | INFO | Изменение роли пользователя |
| `bonus_params_update` | INFO | Изменение параметров премии |
| `export_results` | INFO | Экспорт результатов |
| `system_settings_update` | INFO | Изменение системных настроек |
| `participant_added` | INFO | Добавление участника в сессию |
| `participant_updated` | INFO | Изменение прав участника |
| `participant_removed` | WARN | Удаление участника из сессии |

### 7.3 Экспорт логов

```bash
GET /api/v1/admin/logs/export?format=csv&date_from=2024-10-21&date_to=2024-10-27
Authorization: Bearer {admin_token}
```

### 7.4 Мониторинг подозрительной активности

Система автоматически обнаруживает и логирует:

- **Множественные голосования** с одного IP
- **Изменения оценок** после закрытия сессии
- **Действия неактивных** пользователей
- **Массовые операции** администратора
- **Неудачные попытки входа**

---

## 8. Системные настройки

### 8.1 Просмотр текущих настроек

```bash
GET /api/v1/admin/settings
Authorization: Bearer {admin_token}
```

**Ответ:**
```json
{
  "settings": {
    "vote_scale_min": 0,
    "vote_scale_max": 10,
    "self_vote_weight": 0.8,
    "min_votes_required": 3,
    "session_duration_days": 7,
    "auto_create_sessions": true,
    "session_start_day": "monday",
    "advance_creation_days": 1,
    "auto_add_participants": true,
    "reopen_window_hours": 72,
    "backup_enabled": true,
    "backup_schedule": "0 2 * * *",
    "backup_retention_days": 30,
    "notifications_enabled": true
  }
}
```

### 8.2 Изменение настроек

```bash
PUT /api/v1/admin/settings
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "vote_scale_max": 10,
  "min_votes_required": 5,
  "auto_create_sessions": true,
  "auto_add_participants": true,
  "backup_enabled": true
}
```

### 8.3 Резервное копирование

#### Ручное создание резервной копии
```bash
POST /api/v1/admin/backup/create
Authorization: Bearer {admin_token}
```

**Ответ:**
```json
{
  "status": "success",
  "backup_id": "backup_20241027_120000",
  "filename": "smart_bonus_backup_20241027_120000.sql",
  "size_mb": 45.2,
  "download_url": "/api/v1/admin/backup/download/backup_20241027_120000"
}
```

#### Восстановление из резервной копии
```bash
POST /api/v1/admin/backup/restore
Authorization: Bearer {admin_token}
Content-Type: multipart/form-data

file: {backup_file}
```

---

## 9. Чек-листы администратора

### 9.1 Ежедневные задачи

- [ ] **Проверить журнал ошибок** - `/admin/logs?action=error`
- [ ] **Мониторинг активности голосования** - `/admin/sessions/active`
- [ ] **Проверить участие сотрудников** - просмотреть статистику сессии
- [ ] **Проверить системные уведомления** - важные события системы
- [ ] **Резервное копирование** - убедиться в успешности автоматического бэкапа

### 9.2 Еженедельные задачи

#### В начале недели (понедельник):
- [ ] **Создать сессию на неделю** - если не настроено автоматическое создание
- [ ] **Проверить список участников** - актуальность, добавить новых сотрудников
- [ ] **Установить параметры премии** - на основе данных от бухгалтерии
- [ ] **Проверить список активных сотрудников** - актуальность данных
- [ ] **Отправить уведомление** - о начале голосования

#### В конце недели (пятница-воскресенье):
- [ ] **Мониторинг участия** - напомнить не проголосовавшим
- [ ] **Проверить статусы участников** - актуализировать отпуска/больничные
- [ ] **Закрыть завершённую сессию** - в воскресенье вечером
- [ ] **Проверить расчеты** - автоматические результаты
- [ ] **Экспортировать результаты** - для бухгалтерии

### 9.3 Ежемесячные задачи

- [ ] **Анализ тенденций** - сравнение результатов за месяц
- [ ] **Проверить логи аудита** - анализ активности системы
- [ ] **Обновить список сотрудников** - новые/уволенные сотрудники
- [ ] **Проверить системные настройки** - актуальность конфигурации
- [ ] **Архивация старых данных** - очистка ненужных логов
- [ ] **Анализ участия** - выявление закономерностей в голосовании

### 9.4 Устранение неполадок

#### Частые проблемы и решения:

1. **Сотрудник не может проголосовать**
   - Проверить активность пользователя
   - Проверить права участника в сессии (`can_vote`)
   - Проверить активность сессии
   - Проверить наличие дублирующих голосов

2. **Сотрудник не в списке для голосования**
   - Проверить добавлен ли в участники сессии
   - Проверить статус участника (`active`)
   - Проверить право получать голоса (`can_receive_votes`)

3. **Ошибки при расчёте премии**
   - Проверить установлены ли параметры премии
   - Проверить корректность голосов
   - Запустить перерасчёт результатов

4. **Проблемы с экспортом**
   - Проверить доступ к файловой системе
   - Проверить формат запроса
   - Убедиться что сессия закрыта

5. **Пользователь не найден при авторизации**
   - Проверить наличие пользователя в базе
   - Проверить корректность Telegram ID
   - Создать пользователя вручную при необходимости

### 9.5 Контакты для экстренных случаев

- **Техническая поддержка**: support@company.com
- **Ответственный администратор**: admin@company.com
- **Бухгалтерия**: accounting@company.com
- **HR отдел**: hr@company.com

---

## Приложение: Быстрые команды API

### Управление пользователями
```bash
# Список пользователей
GET /api/v1/admin/users

# Поиск пользователя
GET /api/v1/admin/users/search?query=иван

# Статистика пользователей
GET /api/v1/admin/users/stats
```

### Управление сессиями
```bash
# Список всех сессий
GET /api/v1/admin/sessions

# Быстрое создание сессии на текущую неделю
POST /api/v1/admin/sessions/quick-create

# Статистика по всем сессиям
GET /api/v1/admin/sessions/stats
```

### Управление участниками
```bash
# Участники с правом голосовать
GET /api/v1/admin/sessions/18/participants/can-vote

# Участники которые еще не проголосовали
GET /api/v1/admin/sessions/18/participants/not-voted

# Отправить напоминание не проголосовавшим
POST /api/v1/admin/sessions/18/remind
```

### Экспорт данных
```bash
# Экспорт всех данных за период
GET /api/v1/admin/export/full?date_from=2024-10-01&date_to=2024-10-31