# create-structure.ps1
Write-Host "Создание структуры проекта Smart Bonus Frontend..." -ForegroundColor Green

# Создаем основную структуру папок
$folders = @(
    "public",
    "src/assets/images/icons",
    "src/assets/images/illustrations", 
    "src/assets/styles",
    "src/components/common",
    "src/components/voting",
    "src/components/results",
    "src/components/admin/SessionManagement",
    "src/components/admin/UserManagement",
    "src/components/admin/BonusParams",
    "src/components/admin/VotesManagement",
    "src/components/admin/ExportData",
    "src/components/admin/Analytics",
    "src/components/auth",
    "src/composables",
    "src/stores",
    "src/services/api",
    "src/services/telegram",
    "src/services/storage",
    "src/views/auth",
    "src/views/voting",
    "src/views/results", 
    "src/views/admin",
    "src/views/errors",
    "src/router/routes",
    "src/router/guards",
    "src/utils/date",
    "src/utils/numbers",
    "src/utils/validation/schemas",
    "src/utils/file",
    "src/utils/constants",
    "src/utils/helpers",
    "src/plugins",
    "src/config",
    "tests/unit/components",
    "tests/unit/composables", 
    "tests/unit/utils",
    "tests/unit/stores",
    "tests/e2e",
    "tests/fixtures",
    "docs/components",
    "docs/api",
    "docs/deployment",
    "docs/user-guide",
    "scripts/build",
    "scripts/generate",
    "scripts/utils"
)

foreach ($folder in $folders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "Создана папка: $folder" -ForegroundColor Yellow
    }
}

# Создаем основные файлы
$files = @{
    # Конфигурационные файлы
    "package.json" = @'
{
  "name": "smart-bonus-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.3.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "axios": "^1.4.0",
    "@twa-dev/sdk": "^1.0.2",
    "chart.js": "^4.3.0",
    "vue-chartjs": "^5.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.2.0",
    "vite": "^4.3.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
'@

    "vite.config.js" = @'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000
  }
})
'@

    "tailwind.config.js" = @'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8'
        }
      }
    },
  },
  plugins: [],
}
'@

    # Основные файлы приложения
    "index.html" = @'
<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" href="/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Умная премия</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
'@

    "src/main.js" = @'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { init } from '@twa-dev/sdk'

import App from './App.vue'
import router from './router'
import './style.css'

// Инициализация Telegram WebApp
init()

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
'@

    "src/App.vue" = @'
<template>
  <div class="min-h-screen bg-gray-50">
    <router-view />
  </div>
</template>

<script setup>
// Базовый компонент приложения
</script>
'@

    "src/style.css" = @'
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Кастомные стили для Telegram */
.telegram-bg {
  background: var(--tg-theme-bg-color, #ffffff);
}

.telegram-text {
  color: var(--tg-theme-text-color, #000000);
}

.telegram-button {
  background: var(--tg-theme-button-color, #2481cc);
  color: var(--tg-theme-button-text-color, #ffffff);
}
'@

    # Базовые файлы роутера
    "src/router/index.js" = @'
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { public: true }
  },
  {
    path: '/voting',
    name: 'Voting',
    component: () => import('@/views/voting/VotingView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/results',
    name: 'Results',
    component: () => import('@/views/results/ResultsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/admin/AdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    redirect: '/admin/sessions',
    children: [
      {
        path: 'sessions',
        component: () => import('@/components/admin/SessionManagement/SessionList.vue')
      },
      {
        path: 'users',
        component: () => import('@/components/admin/UserManagement/UserList.vue')
      },
      {
        path: 'bonus-params',
        component: () => import('@/components/admin/BonusParams/BonusForm.vue')
      },
      {
        path: 'votes',
        component: () => import('@/components/admin/VotesManagement/VotesList.vue')
      },
      {
        path: 'export',
        component: () => import('@/components/admin/ExportData/ExportForm.vue')
      },
      {
        path: 'analytics',
        component: () => import('@/components/admin/Analytics/AnalyticsDashboard.vue')
      }
    ]
  },
  {
    path: '/',
    redirect: '/voting'
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/errors/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/voting')
  } else if (to.meta.public && authStore.isAuthenticated) {
    next(authStore.isAdmin ? '/admin' : '/voting')
  } else {
    next()
  }
})

export default router
'@

    # Базовый store
    "src/stores/auth.js" = @'
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/services/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  
  const initAuth = async () => {
    try {
      const initData = window.Telegram?.WebApp?.initData
      if (!initData) throw new Error('No init data')
      
      const response = await authAPI.telegramAuth(initData)
      token.value = response.data.token
      user.value = response.data.user
      
      localStorage.setItem('auth_token', token.value)
      localStorage.setItem('user', JSON.stringify(user.value))
    } catch (error) {
      console.error('Auth error:', error)
      throw error
    }
  }
  
  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
  }
  
  const restoreSession = () => {
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken && savedUser) {
      token.value = savedToken
      user.value = JSON.parse(savedUser)
    }
  }
  
  return {
    user,
    token,
    isAuthenticated,
    isAdmin,
    initAuth,
    logout,
    restoreSession
  }
})
'@

    "src/stores/index.js" = @'
export { useAuthStore } from './auth.js'
// Экспорты других stores будут добавлены позже
'@

    # Базовые сервисы API
    "src/services/api/base.js" = @'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Интерцептор для добавления токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
'@

    "src/services/api/auth.js" = @'
import api from './base'

export const authAPI = {
  telegramAuth: (initData) => 
    api.post('/api/v1/auth/telegram', { init_data: initData }),
}
'@

    # Базовые утилиты
    "src/utils/date/formatters.js" = @'
export const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU')
}

export const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('ru-RU')
}

export const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleTimeString('ru-RU', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

export const getDaysRemaining = (endDate) => {
  const now = new Date()
  const end = new Date(endDate)
  const diff = end - now
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
}
'@

    "src/utils/constants/roles.js" = @'
export const USER_ROLES = {
  USER: 'user',
  MANAGER: 'manager',
  ADMIN: 'admin'
}

export const ROLE_PERMISSIONS = {
  [USER_ROLES.USER]: ['vote:submit', 'results:view'],
  [USER_ROLES.MANAGER]: ['vote:submit', 'results:view', 'users:read', 'exports:read'],
  [USER_ROLES.ADMIN]: ['*']
}

export const ROLE_LABELS = {
  [USER_ROLES.USER]: 'Сотрудник',
  [USER_ROLES.MANAGER]: 'Руководитель',
  [USER_ROLES.ADMIN]: 'Администратор'
}
'@

    # Пустые файлы компонентов (базовые)
    "src/views/auth/LoginView.vue" = @'
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full space-y-8 p-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Вход в систему
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Используйте Telegram для авторизации
        </p>
      </div>
      <div class="mt-8 space-y-6">
        <button
          @click="handleTelegramAuth"
          class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Войти через Telegram
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const handleTelegramAuth = async () => {
  try {
    await authStore.initAuth()
  } catch (error) {
    console.error('Auth failed:', error)
  }
}
</script>
'@

    "src/views/voting/VotingView.vue" = @'
<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-white rounded-lg shadow-sm border">
        <div class="px-6 py-4 border-b">
          <h1 class="text-2xl font-bold text-gray-900 text-center">
            Голосование
          </h1>
          <p class="text-gray-600 text-center mt-2">
            Скоро здесь будет функционал голосования
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Компонент голосования будет реализован
</script>
'@

    "src/views/results/ResultsView.vue" = @'
<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="bg-white rounded-lg shadow-sm border">
        <div class="px-6 py-4 border-b">
          <h1 class="text-2xl font-bold text-gray-900 text-center">
            Результаты
          </h1>
          <p class="text-gray-600 text-center mt-2">
            Скоро здесь будут результаты голосования
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Компонент результатов будет реализован
</script>
'@

    "src/views/admin/AdminView.vue" = @'
<template>
  <div class="min-h-screen bg-gray-100">
    <div class="flex">
      <!-- Sidebar -->
      <div class="w-64 bg-white shadow-sm min-h-screen">
        <div class="p-4 border-b">
          <h2 class="text-lg font-semibold">Админ-панель</h2>
        </div>
        <nav class="mt-4">
          <router-link 
            to="/admin/sessions" 
            class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
          >
            Сессии
          </router-link>
          <router-link 
            to="/admin/users" 
            class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
          >
            Пользователи
          </router-link>
          <router-link 
            to="/admin/bonus-params" 
            class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
          >
            Параметры премии
          </router-link>
          <router-link 
            to="/admin/votes" 
            class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
          >
            Голоса
          </router-link>
          <router-link 
            to="/admin/export" 
            class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
          >
            Экспорт
          </router-link>
          <router-link 
            to="/admin/analytics" 
            class="block px-4 py-2 text-gray-700 hover:bg-gray-100"
          >
            Аналитика
          </router-link>
        </nav>
      </div>
      
      <!-- Main content -->
      <div class="flex-1 p-8">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
// Админская панель будет реализована
</script>
'@

    "src/views/errors/NotFoundView.vue" = @'
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">404</h1>
      <p class="text-xl text-gray-600 mb-8">Страница не найдена</p>
      <router-link 
        to="/" 
        class="text-primary-600 hover:text-primary-500"
      >
        Вернуться на главную
      </router-link>
    </div>
  </div>
</template>

<script setup>
// Страница 404
</script>
'@

    # Другие конфигурационные файлы
    ".env.example" = @'
VITE_API_URL=http://localhost:8000
VITE_APP_NAME="Умная премия"
'@

    ".gitignore" = @'
node_modules/
dist/
dist-ssr/
*.local

# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
'@

    "README.md" = @'
# Smart Bonus Frontend

Фронтенд для системы "Умная премия"

## Установка

1. Установите зависимости:
\`\`\`bash
npm install
\`\`\`

2. Запустите сервер разработки:
\`\`\`bash
npm run dev
\`\`\`

## Структура проекта

Проект использует Vue 3, Pinia для состояния, Vue Router для маршрутизации и Tailwind CSS для стилей.
'@
}

# Создаем файлы
foreach ($file in $files.GetEnumerator()) {
    $filePath = $file.Key
    $content = $file.Value
    
    if (!(Test-Path $filePath)) {
        $content | Out-File -FilePath $filePath -Encoding utf8
        Write-Host "Создан файл: $filePath" -ForegroundColor Green
    } else {
        Write-Host "Файл уже существует: $filePath" -ForegroundColor Gray
    }
}

# Создаем пустые файлы для остальной структуры
$emptyFiles = @(
    "src/components/common/AppHeader.vue",
    "src/components/common/AppFooter.vue",
    "src/components/common/Navigation.vue",
    "src/components/common/StatCard.vue",
    "src/components/common/PieChart.vue",
    "src/components/common/BarChart.vue",
    "src/components/common/DataTable.vue",
    "src/components/common/Modal.vue",
    "src/components/common/Notification.vue",
    "src/components/common/LoadingSpinner.vue",
    "src/components/common/EmptyState.vue",
    "src/components/common/SearchInput.vue",
    "src/components/common/Pagination.vue",
    "src/components/common/FileUpload.vue",
    "src/components/voting/ScoreInput.vue",
    "src/components/voting/VotingForm.vue",
    "src/components/voting/SessionInfo.vue",
    "src/components/voting/VotingProgress.vue",
    "src/components/voting/ColleagueList.vue",
    "src/components/results/ResultsCard.vue",
    "src/components/results/ScoreDistribution.vue",
    "src/components/results/BonusBreakdown.vue",
    "src/components/results/ComparisonChart.vue",
    "src/components/results/PersonalStats.vue",
    "src/components/admin/SessionManagement/SessionList.vue",
    "src/components/admin/SessionManagement/SessionForm.vue",
    "src/components/admin/SessionManagement/SessionCard.vue",
    "src/components/admin/SessionManagement/SessionActions.vue",
    "src/components/admin/SessionManagement/SessionFilters.vue",
    "src/components/admin/UserManagement/UserList.vue",
    "src/components/admin/UserManagement/UserForm.vue",
    "src/components/admin/UserManagement/UserImport.vue",
    "src/components/admin/UserManagement/UserFilters.vue",
    "src/components/admin/UserManagement/UserBulkActions.vue",
    "src/components/admin/BonusParams/BonusForm.vue",
    "src/components/admin/BonusParams/TemplateList.vue",
    "src/components/admin/BonusParams/RevenueCalculator.vue",
    "src/components/admin/BonusParams/BonusPreview.vue",
    "src/components/admin/VotesManagement/VotesList.vue",
    "src/components/admin/VotesManagement/VoteEditor.vue",
    "src/components/admin/VotesManagement/VotesFilters.vue",
    "src/components/admin/VotesManagement/VoteStats.vue",
    "src/components/admin/ExportData/ExportForm.vue",
    "src/components/admin/ExportData/ExportHistory.vue",
    "src/components/admin/ExportData/ReportTemplates.vue",
    "src/components/admin/ExportData/ExportPreview.vue",
    "src/components/admin/Analytics/AnalyticsDashboard.vue",
    "src/components/admin/Analytics/TrendsChart.vue",
    "src/components/admin/Analytics/ParticipationStats.vue",
    "src/components/admin/Analytics/ComparisonView.vue",
    "src/components/admin/Analytics/SessionComparison.vue",
    "src/components/auth/LoginForm.vue",
    "src/components/auth/AuthGuard.vue",
    "src/components/auth/TelegramAuth.vue",
    "src/composables/useVoting.js",
    "src/composables/useResults.js",
    "src/composables/useSessions.js",
    "src/composables/useUsers.js",
    "src/composables/useAuth.js",
    "src/composables/useApi.js",
    "src/composables/useNotifications.js",
    "src/composables/useForm.js",
    "src/composables/usePagination.js",
    "src/composables/useFilters.js",
    "src/composables/useTelegram.js",
    "src/composables/useExport.js",
    "src/composables/useCharts.js",
    "src/composables/useValidation.js",
    "src/stores/voting.js",
    "src/stores/sessions.js",
    "src/stores/users.js",
    "src/stores/results.js",
    "src/stores/notifications.js",
    "src/stores/admin.js",
    "src/services/api/sessions.js",
    "src/services/api/votes.js",
    "src/services/api/results.js",
    "src/services/api/users.js",
    "src/services/api/admin.js",
    "src/services/api/export.js",
    "src/services/telegram/webapp.js",
    "src/services/telegram/notifications.js",
    "src/services/storage/localStorage.js",
    "src/services/storage/fileStorage.js",
    "src/views/voting/SuccessView.vue",
    "src/views/results/PublicResults.vue",
    "src/views/admin/DashboardView.vue",
    "src/views/admin/SessionsView.vue",
    "src/views/admin/UsersView.vue",
    "src/views/admin/VotesView.vue",
    "src/views/admin/ExportView.vue",
    "src/views/admin/AnalyticsView.vue",
    "src/views/errors/UnauthorizedView.vue",
    "src/views/errors/ErrorView.vue",
    "src/router/routes/auth.js",
    "src/router/routes/voting.js",
    "src/router/routes/results.js",
    "src/router/routes/admin.js",
    "src/router/routes/index.js",
    "src/router/guards/auth.js",
    "src/router/guards/admin.js",
    "src/router/guards/session.js",
    "src/utils/date/validators.js",
    "src/utils/date/calculations.js",
    "src/utils/numbers/formatters.js",
    "src/utils/numbers/calculations.js",
    "src/utils/numbers/validators.js",
    "src/utils/validation/schemas/auth.js",
    "src/utils/validation/schemas/voting.js",
    "src/utils/validation/schemas/users.js",
    "src/utils/validation/schemas/sessions.js",
    "src/utils/validation/helpers.js",
    "src/utils/file/download.js",
    "src/utils/file/csv.js",
    "src/utils/file/excel.js",
    "src/utils/constants/app.js",
    "src/utils/constants/sessions.js",
    "src/utils/constants/voting.js",
    "src/utils/constants/api.js",
    "src/utils/helpers/array.js",
    "src/utils/helpers/object.js",
    "src/utils/helpers/string.js",
    "src/utils/helpers/dom.js",
    "src/plugins/telegram.js",
    "src/plugins/notifications.js",
    "src/plugins/api.js",
    "src/plugins/charts.js",
    "src/config/app.js",
    "src/config/api.js",
    "src/config/telegram.js",
    "src/config/theme.js",
    "public/favicon.ico"
)

foreach ($emptyFile in $emptyFiles) {
    if (!(Test-Path $emptyFile)) {
        $directory = Split-Path $emptyFile -Parent
        if (!(Test-Path $directory)) {
            New-Item -ItemType Directory -Path $directory -Force | Out-Null
        }
        New-Item -ItemType File -Path $emptyFile -Force | Out-Null
        Write-Host "Создан пустой файл: $emptyFile" -ForegroundColor Blue
    }
}

Write-Host "`nСтруктура проекта создана успешно!" -ForegroundColor Green
Write-Host "Следующие шаги:" -ForegroundColor Yellow
Write-Host "1. Установите зависимости: npm install" -ForegroundColor White
Write-Host "2. Запустите сервер разработки: npm run dev" -ForegroundColor White
Write-Host "3. Начните разработку с основных компонентов" -ForegroundColor White