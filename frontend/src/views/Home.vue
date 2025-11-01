<template>
  <div class="space-y-6">
    <!-- Заголовок -->
    <div class="text-center">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Добро пожаловать!</h1>
      <p class="text-gray-600">Система еженедельного голосования сотрудников</p>
    </div>

    <!-- Статус текущей сессии -->
    <div v-if="sessionStore.hasActiveSession" class="card">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">Текущая сессия</h2>
        <div class="flex items-center text-green-600">
          <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
          <span class="text-sm font-medium">Активна</span>
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div class="text-center p-3 bg-blue-50 rounded-lg">
          <div class="text-2xl font-bold text-blue-600">{{ sessionStore.sessionDaysLeft }}</div>
          <div class="text-sm text-blue-600">дней осталось</div>
        </div>
        
        <div class="text-center p-3 bg-purple-50 rounded-lg">
          <div class="text-2xl font-bold text-purple-600">{{ sessionStore.votableParticipants.length }}</div>
          <div class="text-sm text-purple-600">участников</div>
        </div>
        
        <div class="text-center p-3 rounded-lg" :class="sessionStore.hasVoted ? 'bg-green-50' : 'bg-orange-50'">
          <div class="text-2xl font-bold" :class="sessionStore.hasVoted ? 'text-green-600' : 'text-orange-600'">
            {{ sessionStore.hasVoted ? '✓' : '!' }}
          </div>
          <div class="text-sm" :class="sessionStore.hasVoted ? 'text-green-600' : 'text-orange-600'">
            {{ sessionStore.hasVoted ? 'Проголосовал' : 'Не голосовал' }}
          </div>
        </div>
      </div>
      
      <!-- Период сессии -->
      <div class="text-sm text-hint mb-4">
        <span>Период: {{ formatDate(sessionStore.currentSession.start_date) }} - {{ formatDate(sessionStore.currentSession.end_date) }}</span>
      </div>
      
      <!-- Кнопки действий -->
      <div class="flex flex-col sm:flex-row gap-3">
        <router-link 
          v-if="sessionStore.canVote" 
          to="/voting" 
          class="btn-primary flex-1 text-center"
        >
          <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          Проголосовать
        </router-link>
        
        <router-link 
          v-else-if="sessionStore.hasVoted" 
          to="/results" 
          class="btn-secondary flex-1 text-center"
        >
          <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          Посмотреть результаты
        </router-link>
        
        <div v-else class="flex-1 p-3 bg-gray-100 rounded-lg text-center text-gray-600">
          <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
          </svg>
          Голосование недоступно
        </div>
      </div>
    </div>

    <!-- Нет активной сессии -->
    <div v-else class="card text-center">
      <div class="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      </div>
      <h3 class="text-lg font-semibold mb-2">Нет активной сессии</h3>
      <p class="text-hint mb-4">В настоящий момент нет открытых сессий голосования</p>
      <button @click="sessionStore.refreshSession" class="btn-secondary">
        <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
        </svg>
        Обновить
      </button>
    </div>

    <!-- Краткая статистика -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Мои результаты -->
      <div class="card">
        <h3 class="text-lg font-semibold mb-3">Мои результаты</h3>
        <div v-if="myStats" class="space-y-2">
          <div class="flex justify-between">
            <span class="text-hint">Лучшее место:</span>
            <span class="font-medium">{{ myStats.bestRank || '—' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-hint">Средняя оценка:</span>
            <span class="font-medium">{{ myStats.avgScore || '—' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-hint">Общий бонус:</span>
            <span class="font-medium">{{ formatCurrency(myStats.totalBonus) || '—' }}</span>
          </div>
        </div>
        <div v-else class="text-center text-hint py-4">
          Нет данных
        </div>
        <router-link to="/results" class="btn-secondary w-full mt-3">
          Подробнее
        </router-link>
      </div>

      <!-- Быстрые действия -->
      <div class="card">
        <h3 class="text-lg font-semibold mb-3">Быстрые действия</h3>
        <div class="space-y-2">
          <router-link to="/history" class="btn-secondary w-full text-left flex items-center">
            <svg class="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            История сессий
          </router-link>
          
          <router-link to="/profile" class="btn-secondary w-full text-left flex items-center">
            <svg class="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
            Мой профиль
          </router-link>
          
          <router-link 
            v-if="authStore.isAdmin" 
            to="/admin" 
            class="btn-secondary w-full text-left flex items-center"
          >
            <svg class="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            Администрирование
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useSessionStore } from '../stores/session'
import { api } from '../services/api'

const authStore = useAuthStore()
const sessionStore = useSessionStore()
const myStats = ref(null)

// Вычисляемые
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('ru-RU')
}

const formatCurrency = (amount) => {
  if (!amount) return '0 ₽'
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB'
  }).format(amount)
}

// Методы
const loadMyStats = async () => {
  try {
    const response = await api.results.me()
    if (response.data.status === 'success') {
      const results = response.data.results || []
      
      if (results.length > 0) {
        myStats.value = {
          bestRank: Math.min(...results.map(r => r.rank)),
          avgScore: (results.reduce((sum, r) => sum + r.average_score, 0) / results.length).toFixed(1),
          totalBonus: results.reduce((sum, r) => sum + r.total_bonus, 0)
        }
      }
    }
  } catch (error) {
    console.error('Ошибка загрузки статистики:', error)
  }
}

// Жизненный цикл
onMounted(() => {
  loadMyStats()
})
</script>
