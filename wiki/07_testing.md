# Тестирование системы «Умная премия»

## Содержание
1. [Стратегия тестирования](#1-стратегия-тестирования)
2. [Тестовое окружение](#2-тестовое-окружение)
3. [Функциональное тестирование](#3-функциональное-тестирование)
4. [Интеграционное тестирование](#4-интеграционное-тестирование)
5. [Нагрузочное тестирование](#5-нагрузочное-тестирование)
6. [Безопасность](#6-безопасность)
7. [Автоматизированные тесты](#7-автоматизированные-тесты)
8. [Чек-листы ручного тестирования](#8-чек-листы-ручного-тестирования)

---

## 1. Стратегия тестирования

### 1.1 Уровни тестирования

```mermaid
graph TB
    A[Unit Tests] --> B[Integration Tests]
    B --> C[API Tests]
    C --> D[E2E Tests]
    D --> E[Performance Tests]
    E --> F[Security Tests]
```

### 1.2 Критерии качества

- **Функциональность**: 100% покрытие основных сценариев
- **Производительность**: < 2 сек на операцию, < 5 сек на расчет премии
- **Безопасность**: OWASP Top 10 compliance
- **Надежность**: 99.9% uptime, корректное восстановление после сбоев

---

## 2. Тестовое окружение

### 2.1 Конфигурация

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: smart_bonus_test
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    ports:
      - "5433:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"

  api:
    build: .
    environment:
      NODE_ENV: test
      DATABASE_URL: postgresql://test:test@postgres:5432/smart_bonus_test
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
```

### 2.2 Скрипты запуска

```bash
#!/bin/bash
# scripts/test-setup.sh

echo "🚀 Запуск тестового окружения..."

# Остановка и очистка
docker-compose -f docker-compose.test.yml down
docker volume prune -f

# Запуск сервисов
docker-compose -f docker-compose.test.yml up -d

# Ожидание готовности БД
until docker exec smart_bonus_postgres_1 pg_isready -U test; do
  sleep 1
done

# Загрузка тестовых данных
npm run db:seed:test

echo "✅ Тестовое окружение готово"
```

---

## 3. Функциональное тестирование

### 3.1 Тест-кейсы: Авторизация

| ID | Название | Предусловия | Шаги | Ожидаемый результат |
|----|----------|-------------|------|---------------------|
| AUTH-01 | Успешная авторизация через Telegram | Пользователь существует в системе | 1. Отправить initData<br>2. Получить токен | Статус 200, валидный JWT токен |
| AUTH-02 | Авторизация нового пользователя | Пользователь не существует | 1. Отправить initData нового пользователя | Статус 404, сообщение "Пользователь не найден" |
| AUTH-03 | Невалидная подпись Telegram | - | 1. Отправить поддельный initData | Статус 401, "Неверная подпись Telegram" |
| AUTH-04 | Просроченный токен | Токен истек | 1. Использовать просроченный токен | Статус 403, "Токен истек" |

### 3.2 Тест-кейсы: Управление сессиями

| ID | Название | Предусловия | Шаги | Ожидаемый результат |
|----|----------|-------------|------|---------------------|
| SESS-01 | Создание сессии | Пользователь - админ | 1. POST /sessions с датами | Статус 201, создана сессия с участниками |
| SESS-02 | Закрытие сессии | Активная сессия существует | 1. POST /sessions/{id}/close | Статус 200, сессия закрыта, расчет результатов |
| SESS-03 | Повторное открытие | Сессия закрыта < 72ч назад | 1. POST /sessions/{id}/reopen | Статус 200, сессия активна, новые даты |
| SESS-04 | Просмотр активной сессии | - | 1. GET /sessions/current | Статус 200, данные активной сессии |

### 3.3 Тест-кейсы: Голосование

| ID | Название | Предусловия | Шаги | Ожидаемый результат |
|----|----------|-------------|------|---------------------|
| VOTE-01 | Успешное голосование | Пользователь может голосовать | 1. POST /votes с оценками | Статус 200, голоса сохранены |
| VOTE-02 | Голосование за себя | - | 1. Отправить голос за себя | Статус 200, самооценка сохранена |
| VOTE-03 | Дублирование голоса | Уже голосовал за сотрудника | 1. Повторный голос за того же | Статус 409, "Уже голосовали" |
| VOTE-04 | Голосование без прав | Пользователь can_vote=false | 1. Попытка голосования | Статус 403, "Нет прав" |

### 3.4 Тест-кейсы: Расчет премии

| ID | Название | Предусловия | Шаги | Ожидаемый результат |
|----|----------|-------------|------|---------------------|
| BONUS-01 | Расчет с параметрами | Голоса есть, параметры установлены | 1. Закрыть сессию | Корректный расчет _T1-_T4, распределение премии |
| BONUS-02 | Расчет без параметров | Голоса есть, параметров нет | 1. Закрыть сессию | Статус 422, "Нет параметров премии" |
| BONUS-03 | Проверка пропорций | 3 пользователя с разными оценками | 1. Расчет премии | Сумма премий = total_weekly_bonus |
| BONUS-04 | Нулевые оценки | Все оценки = 0 | 1. Расчет премии | Равномерное распределение или ошибка |

---

## 4. Интеграционное тестирование

### 4.1 Поток полного голосования

```javascript
// tests/integration/full-voting-flow.test.js
describe('Полный поток голосования', () => {
  test('Создание сессии → Голосование → Расчет → Экспорт', async () => {
    // 1. Создание сессии
    const session = await api.createSession({
      start_date: '2024-01-01',
      end_date: '2024-01-07'
    });
    
    // 2. Установка параметров премии
    await api.setBonusParams(session.id, {
      total_weekly_bonus: 10000,
      participation_multiplier: 0.8
    });
    
    // 3. Голосование нескольких пользователей
    await api.vote(user1Token, session.id, [
      { user_id: 102, score: 8 },
      { user_id: 103, score: 9 }
    ]);
    
    await api.vote(user2Token, session.id, [
      { user_id: 101, score: 7 },
      { user_id: 103, score: 8 }
    ]);
    
    // 4. Закрытие сессии и расчет
    const results = await api.closeSession(session.id);
    
    // 5. Проверка результатов
    expect(results.summary.total_bonus_distributed).toBe(10000);
    expect(results.results).toHaveLength(3);
    
    // 6. Экспорт результатов
    const exportData = await api.exportResults(session.id);
    expect(exportData).toContain('ФИО,Премия');
  });
});
```

### 4.2 Интеграция с Telegram

```javascript
// tests/integration/telegram-auth.test.js
describe('Интеграция с Telegram', () => {
  test('Валидация WebApp данных', async () => {
    const validInitData = generateValidInitData();
    const response = await api.authTelegram(validInitData);
    
    expect(response.status).toBe(200);
    expect(response.data.token).toBeDefined();
    expect(response.data.user.telegram_id).toBe(123456789);
  });
  
  test('Отклонение невалидной подписи', async () => {
    const invalidInitData = generateInvalidInitData();
    const response = await api.authTelegram(invalidInitData);
    
    expect(response.status).toBe(401);
    expect(response.data.message).toContain('Неверная подпись');
  });
});
```

---

## 5. Нагрузочное тестирование

### 5.1 Сценарии нагрузки

```javascript
// tests/load/voting-load.test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },  // Постепенный рост
    { duration: '5m', target: 50 },  // Стабильная нагрузка
    { duration: '2m', target: 100 }, // Пиковая нагрузка
    { duration: '2m', target: 0 },   // Снижение
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% запросов < 2 сек
    http_req_failed: ['rate<0.01'],    // < 1% ошибок
  },
};

export default function () {
  // Аутентификация
  const authRes = http.post(`${BASE_URL}/auth/telegram`, {
    init_data: generateInitData()
  });
  
  const token = authRes.json('token');
  
  // Получение активной сессии
  const sessionRes = http.get(`${BASE_URL}/sessions/current`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const sessionId = sessionRes.json('session_id');
  
  // Голосование
  const votePayload = JSON.stringify({
    session_id: sessionId,
    votes: generateRandomVotes()
  });
  
  const voteRes = http.post(`${BASE_URL}/votes`, votePayload, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  // Проверки
  check(voteRes, {
    'vote successful': (r) => r.status === 200,
    'response time OK': (r) => r.timings.duration < 1000
  });
  
  sleep(1);
}
```

### 5.2 Тестирование расчета премии

```javascript
// tests/load/calculation-load.test.js
export const options = {
  scenarios: {
    calculation_stress: {
      executor: 'per-vu-iterations',
      vus: 10,
      iterations: 20,
      maxDuration: '10m',
    },
  },
};

export default function () {
  // Создание сессии с большим количеством участников
  const sessionRes = http.post(`${BASE_URL}/admin/sessions`, {
    start_date: '2024-01-01',
    end_date: '2024-01-07',
    auto_participants: true
  }, {
    headers: { 'Authorization': `Bearer ${ADMIN_TOKEN}` }
  });
  
  const sessionId = sessionRes.json('session_id');
  
  // Массовое голосование (эмулируем 100 участников)
  for (let i = 0; i < 100; i++) {
    const votePayload = JSON.stringify({
      session_id: sessionId,
      votes: generateMassVotes()
    });
    
    http.post(`${BASE_URL}/votes`, votePayload, {
      headers: { 'Authorization': `Bearer ${USER_TOKENS[i]}` }
    });
  }
  
  // Расчет результатов
  const calcRes = http.post(`${BASE_URL}/admin/sessions/${sessionId}/close`, {}, {
    headers: { 'Authorization': `Bearer ${ADMIN_TOKEN}` }
  });
  
  check(calcRes, {
    'calculation completed': (r) => r.status === 200,
    'calculation time < 5s': (r) => r.timings.duration < 5000
  });
}
```

---

## 6. Безопасность

### 6.1 Тесты безопасности API

```javascript
// tests/security/api-security.test.js
describe('Безопасность API', () => {
  test('Защита от SQL-инъекций', async () => {
    const maliciousPayload = {
      session_id: "1; DROP TABLE users; --",
      votes: [{ user_id: "101 OR 1=1", score: 10 }]
    };
    
    const response = await api.vote(userToken, maliciousPayload);
    expect(response.status).not.toBe(500);
    // Должна быть валидационная ошибка, а не SQL ошибка
  });
  
  test('Защита от XSS', async () => {
    const xssPayload = {
      name: "<script>alert('xss')</script>",
      user_id: 999
    };
    
    const response = await api.createUser(adminToken, xssPayload);
    // Имя должно быть санитизировано или отклонено
    expect(response.data.name).not.toContain('<script>');
  });
  
  test('Проверка CORS', async () => {
    const response = await api.request('OPTIONS', '/votes', {
      headers: {
        'Origin': 'http://malicious-site.com',
        'Access-Control-Request-Method': 'POST'
      }
    });
    
    // Должны разрешаться только доверенные домены
    expect(response.headers['access-control-allow-origin']).not.toBe('*');
  });
});
```

### 6.2 Тесты авторизации и прав

```javascript
// tests/security/authorization.test.js
describe('Проверка прав доступа', () => {
  test('Обычный пользователь не может создавать сессии', async () => {
    const response = await api.createSession(userToken, {
      start_date: '2024-01-01',
      end_date: '2024-01-07'
    });
    
    expect(response.status).toBe(403);
  });
  
  test('Пользователь не может видеть чужие результаты', async () => {
    const response = await api.getResults(userToken, 'other-user-id');
    expect(response.status).toBe(403);
  });
  
  test('Менеджер может видеть результаты команды', async () => {
    const response = await api.getTeamResults(managerToken);
    expect(response.status).toBe(200);
  });
});
```

---

## 7. Автоматизированные тесты

### 7.1 Unit-тесты

```javascript
// tests/unit/bonus-calculation.test.js
import { calculateSessionResults } from '../../src/services/bonus-calculation';

describe('Расчет премии', () => {
  test('Корректное распределение премии', () => {
    const votes = [
      { voter_id: 1, target_id: 2, score: 8 },
      { voter_id: 2, target_id: 1, score: 9 },
      { voter_id: 3, target_id: 1, score: 7 }
    ];
    
    const params = {
      total_weekly_bonus: 1000,
      participation_multiplier: 1.0
    };
    
    const results = calculateSessionResults(votes, params);
    
    expect(results[1].total_bonus).toBeGreaterThan(results[2].total_bonus);
    expect(results.reduce((sum, r) => sum + r.total_bonus, 0)).toBe(1000);
  });
  
  test('Обработка нулевых оценок', () => {
    const votes = [
      { voter_id: 1, target_id: 2, score: 0 },
      { voter_id: 2, target_id: 1, score: 0 }
    ];
    
    const results = calculateSessionResults(votes, { total_weekly_bonus: 1000 });
    
    // Должно быть равномерное распределение или ошибка
    expect(results.every(r => r.total_bonus === 500)).toBe(true);
  });
});
```

### 7.2 API-тесты с Jest и Supertest

```javascript
// tests/api/votes.api.test.js
const request = require('supertest');
const app = require('../../src/app');
const db = require('../../src/db');

describe('API Votes', () => {
  beforeAll(async () => {
    await db.migrate.latest();
    await db.seed.run();
  });
  
  afterAll(async () => {
    await db.destroy();
  });
  
  describe('POST /api/v1/votes', () => {
    test('Успешное сохранение голосов', async () => {
      const response = await request(app)
        .post('/api/v1/votes')
        .set('Authorization', `Bearer ${userToken}`)
        .send({
          session_id: 1,
          votes: [
            { user_id: 2, score: 8 },
            { user_id: 3, score: 9 }
          ]
        });
      
      expect(response.status).toBe(200);
      expect(response.body.status).toBe('success');
    });
    
    test('Валидация оценки (0-10)', async () => {
      const response = await request(app)
        .post('/api/v1/votes')
        .set('Authorization', `Bearer ${userToken}`)
        .send({
          session_id: 1,
          votes: [{ user_id: 2, score: 11 }] // Невалидная оценка
        });
      
      expect(response.status).toBe(400);
      expect(response.body.message).toContain('диапазоне 0-10');
    });
  });
});
```

### 7.3 E2E-тесты с Playwright

```javascript
// tests/e2e/voting.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Процесс голосования', () => {
  test('Полный цикл голосования', async ({ page }) => {
    // 1. Авторизация
    await page.goto('/');
    await page.click('text=Войти через Telegram');
    
    // 2. Выбор сессии
    await page.waitForSelector('.session-card');
    await page.click('.session-card:first-child');
    
    // 3. Голосование
    await page.fill('input[data-user-id="101"]', '8');
    await page.fill('input[data-user-id="102"]', '9');
    await page.click('button[type="submit"]');
    
    // 4. Проверка успешного голосования
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('text=Оценки сохранены')).toBeVisible();
    
    // 5. Просмотр результатов
    await page.click('text=Мои результаты');
    await expect(page.locator('.results-table')).toBeVisible();
  });
});
```

### 7.4 Скрипты запуска тестов

```json
// package.json
{
  "scripts": {
    "test:unit": "jest tests/unit --coverage",
    "test:api": "jest tests/api --runInBand",
    "test:integration": "jest tests/integration --runInBand",
    "test:e2e": "playwright test",
    "test:load": "k6 run tests/load/voting-load.test.js",
    "test:security": "jest tests/security",
    "test:all": "npm run test:unit && npm run test:api && npm run test:integration",
    "test:ci": "npm run test:all -- --ci --coverage --verbose"
  }
}
```

---

## 8. Чек-листы ручного тестирования

### 8.1 Чек-лист приемочного тестирования

**Функциональность голосования**
- [ ] Авторизация через Telegram работает корректно
- [ ] Отображение активной сессии
- [ ] Список сотрудников для голосования загружается
- [ ] Оценки сохраняются (0-10)
- [ ] Нельзя голосовать дважды за одного сотрудника
- [ ] Самооценка работает корректно
- [ ] Подтверждение успешного голосования

**Административная панель**
- [ ] Создание/закрытие сессий
- [ ] Управление участниками сессии
- [ ] Установка параметров премии
- [ ] Просмотр всех голосов
- [ ] Корректировка оценок
- [ ] Экспорт результатов (XLSX/CSV)

**Расчет премии**
- [ ] Автоматический расчет при закрытии сессии
- [ ] Корректность расчетов _T1-_T4
- [ ] Пропорциональное распределение премии
- [ ] Обработка крайних случаев (все 0, все 10)

### 8.2 Чек-лист UI/UX тестирования

**Веб-интерфейс**
- [ ] Адаптивность (мобильные/десктоп)
- [ ] Доступность (screen readers)
- [ ] Валидация форм в реальном времени
- [ ] Информативные сообщения об ошибках
- [ ] Loading states для всех операций

**Telegram WebApp**
- [ ] Корректное отображение в Telegram
- [ ] Поддержка тем (light/dark)
- [ ] Навигация жестами
- [ ] Оптимизация для мобильных

### 8.3 Чек-лист регрессионного тестирования

**Критические сценарии**
- [ ] Авторизация нового и существующего пользователя
- [ ] Голосование в активной сессии
- [ ] Расчет премии с различными параметрами
- [ ] Экспорт результатов
- [ ] Управление пользователями (админ)

**Пограничные случаи**
- [ ] Голосование в последний день сессии
- [ ] Сессия без участников
- [ ] Пользователь без прав голоса
- [ ] Одновременное голосование нескольких пользователей

### 8.4 Чек-лист производительности

**Время отклика**
- [ ] Загрузка списка сотрудников: < 2 сек
- [ ] Сохранение голосов: < 1 сек
- [ ] Расчет премии (100 участников): < 5 сек
- [ ] Экспорт результатов: < 3 сек

**Нагрузка**
- [ ] 50 одновременных пользователей
- [ ] 1000 голосов в сессии
- [ ] Стабильность при пиковой нагрузке

---

## 9. Мониторинг и метрики

### 9.1 Ключевые метрики для мониторинга

```javascript
// metrics to track
const metrics = {
  performance: {
    'api.response_time': 'p95 < 2s',
    'vote.processing_time': 'p95 < 1s',
    'calculation.duration': 'p95 < 5s'
  },
  business: {
    'sessions.active': 'count',
    'votes.per_session': 'average',
    'participation.rate': 'percentage',
    'users.active': 'count'
  },
  errors: {
    'auth.failures': 'rate',
    'vote.validation_errors': 'count',
    'calculation.errors': 'count'
  }
};
```

Этот план тестирования обеспечивает полное покрытие функциональности системы «Умная премия» и гарантирует высокое качество перед запуском в продакшн. 🚀