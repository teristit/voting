<template>
  <div class="space-y-6">
    <!-- Заголовок -->
    <div class="text-center">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Результаты</h1>
      <p class="text-gray-600">Результаты текущей сессии голосования</p>
    </div>

    <!-- Нет активной сессии -->
    <div v-if="!sessionStore.hasActiveSession" class="card text-center">
      <div class="text-gray-400 mb-2">
        <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
        </svg>
      </div>
      <h3 class="text-lg font-semibold mb-2">Нет активной сессии</h3>
      <p class="text-hint">Результаты будут доступны после завершения сессии голосования</p>
    </div>

    <!-- Результаты еще не подсчитаны -->
    <div v-else-if="!results || results.length === 0" class="card text-center">
      <div class="text-blue-500 mb-2">
        <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      </div>
      <h3 class="text-lg font-semibold mb-2">Результаты готовятся</h3>
      <p class="text-hint mb-4">Пожалуйста, подождите. Результаты будут доступны после обработки всех голосов</p>
      <button @click="loadResults" class="btn-primary" :disabled="loading">
        {{ loading ? 'Загрузка...' : 'Обновить' }}
      </button>
    </div>

    <!-- Таблица результатов -->
    <div v-else class="space-y-4">
      <!-- Информация о сессии -->
      <div class="card">
        <h3 class="text-lg font-semibold mb-3">Информация о сессии</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="text-center p-3 bg-blue-50 rounded-lg">
            <div class="text-2xl font-bold text-blue-600">{{ results.length }}</div>
            <div class="text-sm text-blue-600">участников</div>
          </div>
          <div class="text-center p-3 bg-green-50 rounded-lg">
            <div class="text-2xl font-bold text-green-600">{{ totalBonus }}</div>
            <div class="text-sm text-green-600">общий бонус</div>
          </div>
          <div class="text-center p-3 bg-purple-50 rounded-lg">
            <div class="text-2xl font-bold text-purple-600">{{ averageScore }}</div>
            <div class="text-sm text-purple-600">средняя оценка</div>
          </div>
        </div>
      </div>

      <!-- Топ-3 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div 
          v-for="(result, index) in results.slice(0, 3)" 
          :key="result.user_id"
          class="card text-center"
          :class="{
            'bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200': index === 0,
            'bg-gradient-to-br from-gray-50 to-gray-100 border-gray-200': index === 1,
            'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200': index === 2
          }"
        >
          <div class="mb-3">
            <div class="text-3xl mb-2">
              {{ index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉' }}
            </div>
            <div class="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mx-auto">
              <span class="text-white font-semibold">{{ getInitials(result.name) }}</span>
            </div>
          </div>
          <h3 class="font-semibold text-lg mb-1">{{ result.name }}</h3>
          <div class="text-2xl font-bold text-blue-600 mb-1">{{ result.average_score.toFixed(1) }}</div>
          <div class="text-sm text-hint mb-2">{{ result.votes_received }} голосов</div>
          <div class="text-lg font-semibold text-green-600">{{ formatCurrency(result.total_bonus) }}</div>
        </div>
      </div>

      <!-- Полная таблица результатов -->
      <div class="card overflow-hidden">
        <h3 class="text-lg font-semibold mb-4">Полные результаты</h3>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Место</th>
                <th class="px-4 py-3 text-left text-sm font-medium text-gray-500">Участник</th>
                <th class="px-4 py-3 text-center text-sm font-medium text-gray-500">Оценка</th>
                <th class="px-4 py-3 text-center text-sm font-medium text-gray-500">Голосов</th>
                <th class="px-4 py-3 text-right text-sm font-medium text-gray-500">Бонус</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr 
                v-for="result in results" 
                :key="result.user_id"
                :class="{
                  'bg-blue-50': result.user_id === authStore.user?.user_id
                }"
              >
                <td class="px-4 py-3">
                  <div class="flex items-center">
                    <span class="font-semibold text-lg">{{ result.rank }}</span>
                    <span v-if="result.rank <= 3" class="ml-2 text-lg">
                      {{ result.rank === 1 ? '🥇' : result.rank === 2 ? '🥈' : '🥉' }}
                    </span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div class="flex items-center space-x-3">
                    <div class="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <span class="text-white font-semibold text-xs">{{ getInitials(result.name) }}</span>
                    </div>
                    <div>
                      <div class="font-medium">{{ result.name }}</div>
                      <div v-if="result.user_id === authStore.user?.user_id" class="text-xs text-blue-600 font-medium">
                        Это вы
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3 text-center">
                  <span class="text-lg font-semibold text-blue-600">{{ result.average_score.toFixed(1) }}</span>
                </td>
                <td class="px-4 py-3 text-center">
                  <span class="text-gray-600">{{ result.votes_received }}</span>
                </td>
                <td class="px-4 py-3 text-right">
                  <span class="font-semibold text-green-600">{{ formatCurrency(result.total_bonus) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useSessionStore } from '../stores/session'

const authStore = useAuthStore()
const sessionStore = useSessionStore()

// Состояние
const results = ref([])
const loading = ref(false)

// Вычисляемые
const totalBonus = computed(() => {
  if (!results.value || results.value.length === 0) return '0 ₽'
  const total = results.value.reduce((sum, result) => sum + result.total_bonus, 0)
  return formatCurrency(total)
})

const averageScore = computed(() => {
  if (!results.value || results.value.length === 0) return '0.0'
  const average = results.value.reduce((sum, result) => sum + result.average_score, 0) / results.value.length
  return average.toFixed(1)
})

// Методы
const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(word => word[0]).join('').toUpperCase().substring(0, 2)
}

const formatCurrency = (amount) => {
  if (!amount) return '0 ₽'
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB'
  }).format(amount)
}

const loadResults = async () => {
  if (!sessionStore.currentSession?.session_id) return
  
  loading.value = true
  try {
    const sessionResults = await sessionStore.loadSessionResults()
    if (sessionResults) {
      results.value = sessionResults
    }
  } catch (error) {
    console.error('Ошибка загрузки результатов:', error)
  } finally {
    loading.value = false
  }
}

// Жизненный цикл
onMounted(() => {
  loadResults()
})
</script>