<template>
  <div class="space-y-6">
    <!-- Заголовок -->
    <div class="text-center">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Мой профиль</h1>
      <p class="text-gray-600">Информация о пользователе и статистика</p>
    </div>

    <!-- Информация о пользователе -->
    <div class="card">
      <div class="flex items-center space-x-4 mb-6">
        <div class="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center">
          <span class="text-white font-semibold text-xl">{{ getInitials(authStore.user?.name) }}</span>
        </div>
        <div>
          <h2 class="text-xl font-semibold">{{ authStore.user?.name }}</h2>
          <p class="text-hint">@{{ authStore.user?.telegram_username || 'user' }}</p>
          <div class="flex items-center mt-1">
            <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                  :class="{
                    'bg-green-100 text-green-800': authStore.user?.active,
                    'bg-red-100 text-red-800': !authStore.user?.active
                  }">
              {{ authStore.user?.active ? 'Активен' : 'Неактивен' }}
            </span>
            <span class="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              {{ getRoleLabel(authStore.user?.role) }}
            </span>
          </div>
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="text-center p-4 bg-blue-50 rounded-lg">
          <div class="text-2xl font-bold text-blue-600">{{ stats.sessionsParticipated || 0 }}</div>
          <div class="text-sm text-blue-600">сессий участвовал</div>
        </div>
        <div class="text-center p-4 bg-green-50 rounded-lg">
          <div class="text-2xl font-bold text-green-600">{{ stats.averageRank || '—' }}</div>
          <div class="text-sm text-green-600">среднее место</div>
        </div>
        <div class="text-center p-4 bg-purple-50 rounded-lg">
          <div class="text-2xl font-bold text-purple-600">{{ formatCurrency(stats.totalBonus) }}</div>
          <div class="text-sm text-purple-600">общий бонус</div>
        </div>
      </div>
    </div>

    <!-- Настройки уведомлений -->
    <div class="card">
      <h3 class="text-lg font-semibold mb-4">Настройки</h3>
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <div class="font-medium">Уведомления в Telegram</div>
            <div class="text-sm text-hint">Получать уведомления о новых сессиях и результатах</div>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="settings.notifications" class="sr-only peer">
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
        
        <div class="flex items-center justify-between">
          <div>
            <div class="font-medium">Напоминания о голосовании</div>
            <div class="text-sm text-hint">Напоминать о необходимости проголосовать</div>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input type="checkbox" v-model="settings.reminders" class="sr-only peer">
            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
      </div>
      
      <div class="mt-6 pt-4 border-t border-gray-200">
        <button @click="saveSettings" class="btn-primary" :disabled="saving">
          {{ saving ? 'Сохранение...' : 'Сохранить настройки' }}
        </button>
      </div>
    </div>

    <!-- Действия -->
    <div class="card">
      <h3 class="text-lg font-semibold mb-4">Действия</h3>
      <div class="space-y-3">
        <button @click="exportData" class="btn-secondary w-full text-left flex items-center justify-between">
          <div class="flex items-center">
            <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Экспорт моих данных
          </div>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </button>
        
        <button @click="clearCache" class="btn-secondary w-full text-left flex items-center justify-between">
          <div class="flex items-center">
            <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            Очистить кэш
          </div>
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { api } from '../services/api'

const authStore = useAuthStore()

// Состояние
const stats = ref({
  sessionsParticipated: 0,
  averageRank: null,
  totalBonus: 0
})

const settings = ref({
  notifications: true,
  reminders: true
})

const saving = ref(false)

// Методы
const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(word => word[0]).join('').toUpperCase().substring(0, 2)
}

const getRoleLabel = (role) => {
  const labels = {
    'admin': 'Администратор',
    'user': 'Пользователь'
  }
  return labels[role] || 'Пользователь'
}

const formatCurrency = (amount) => {
  if (!amount) return '0 ₽'
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB'
  }).format(amount)
}

const loadStats = async () => {
  try {
    const response = await api.results.me()
    if (response.data.status === 'success') {
      const results = response.data.results || []
      
      if (results.length > 0) {
        stats.value = {
          sessionsParticipated: results.length,
          averageRank: (results.reduce((sum, r) => sum + r.rank, 0) / results.length).toFixed(1),
          totalBonus: results.reduce((sum, r) => sum + r.total_bonus, 0)
        }
      }
    }
  } catch (error) {
    console.error('Ошибка загрузки статистики:', error)
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    // Здесь будет вызов API для сохранения настроек
    await new Promise(resolve => setTimeout(resolve, 1000)) // Заглушка
    
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.showAlert('Настройки сохранены!')
    }
  } catch (error) {
    console.error('Ошибка сохранения настроек:', error)
  } finally {
    saving.value = false
  }
}

const exportData = async () => {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.showAlert('Функция экспорта данных будет доступна в ближайшее время')
  }
}

const clearCache = () => {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.showConfirm('Очистить кэш приложения?', (confirmed) => {
      if (confirmed) {
        localStorage.clear()
        window.location.reload()
      }
    })
  } else {
    if (confirm('Очистить кэш приложения?')) {
      localStorage.clear()
      window.location.reload()
    }
  }
}

// Жизненный цикл
onMounted(() => {
  loadStats()
})
</script>