<template>
  <div class="space-y-6">
    <!-- Заголовок -->
    <div class="text-center">
      <h1 class="text-2xl font-bold text-gray-900 mb-2">Голосование</h1>
      <p class="text-gray-600">Оцените работу своих коллег по шкале от 0 до 10</p>
    </div>

    <!-- Прогресс -->
    <div class="card">
      <div class="flex items-center justify-between mb-2">
        <span class="text-sm font-medium">Прогресс голосования</span>
        <span class="text-sm text-hint">{{ votedCount }}/{{ totalVotes }}</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div 
          class="bg-blue-500 h-2 rounded-full transition-all duration-300" 
          :style="{ width: `${progressPercentage}%` }"
        ></div>
      </div>
    </div>

    <!-- Нет участников -->
    <div v-if="!sessionStore.hasActiveSession" class="card text-center">
      <div class="text-gray-400 mb-2">
        <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      </div>
      <h3 class="text-lg font-semibold mb-2">Нет активной сессии</h3>
      <p class="text-hint">Голосование в настоящий момент недоступно</p>
    </div>

    <!-- Уже проголосовал -->
    <div v-else-if="sessionStore.hasVoted" class="card text-center">
      <div class="text-green-500 mb-2">
        <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
      </div>
      <h3 class="text-lg font-semibold mb-2">Вы уже проголосовали!</h3>
      <p class="text-hint mb-4">Спасибо за участие в голосовании</p>
      <router-link to="/results" class="btn-primary">
        Посмотреть результаты
      </router-link>
    </div>

    <!-- Нельзя голосовать -->
    <div v-else-if="!sessionStore.canVote" class="card text-center">
      <div class="text-orange-500 mb-2">
        <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
        </svg>
      </div>
      <h3 class="text-lg font-semibold mb-2">Голосование недоступно</h3>
      <p class="text-hint">У вас нет прав для голосования в этой сессии</p>
    </div>

    <!-- Форма голосования -->
    <div v-else-if="sessionStore.votableParticipants.length > 0">
      <!-- Участники -->
      <div class="space-y-4">
        <div 
          v-for="participant in sessionStore.votableParticipants" 
          :key="participant.user_id"
          class="card"
        >
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                <span class="text-white font-semibold text-sm">
                  {{ getInitials(participant.name) }}
                </span>
              </div>
              <div>
                <h3 class="font-semibold">{{ participant.name }}</h3>
                <p class="text-sm text-hint">@{{ participant.telegram_username || 'user' }}</p>
              </div>
            </div>
            
            <!-- Текущая оценка -->
            <div class="text-right">
              <div class="text-2xl font-bold text-blue-600">
                {{ votes[participant.user_id] !== undefined ? votes[participant.user_id] : '?' }}
              </div>
              <div class="text-xs text-hint">оценка</div>
            </div>
          </div>
          
          <!-- Шкала оценок -->
          <div class="mb-3">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm text-hint">Оценка от 0 до 10</span>
              <span class="text-sm text-blue-600">
                {{ votes[participant.user_id] !== undefined ? 
                   getScoreLabel(votes[participant.user_id]) : 'Не оценено' }}
              </span>
            </div>
            
            <div class="grid grid-cols-11 gap-1">
              <button
                v-for="score in 11"
                :key="score - 1"
                @click="setVote(participant.user_id, score - 1)"
                class="h-10 rounded text-sm font-medium transition-all duration-200"
                :class="{
                  'bg-blue-500 text-white': votes[participant.user_id] === (score - 1),
                  'bg-gray-100 hover:bg-gray-200 text-gray-700': votes[participant.user_id] !== (score - 1)
                }"
              >
                {{ score - 1 }}
              </button>
            </div>
          </div>
          
          <!-- Комментарий (опционально) -->
          <div>
            <textarea
              v-model="comments[participant.user_id]"
              placeholder="Комментарий (опционально)"
              class="input-primary resize-none"
              rows="2"
              :maxlength="500"
            ></textarea>
          </div>
        </div>
      </div>
      
      <!-- Кнопки действий -->
      <div class="sticky bottom-4 bg-white p-4 rounded-lg shadow-lg border">
        <div class="flex flex-col sm:flex-row gap-3">
          <button 
            @click="submitVotes" 
            :disabled="!canSubmit || sessionStore.votingInProgress"
            class="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="sessionStore.votingInProgress" class="animate-spin w-4 h-4 inline mr-2" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ sessionStore.votingInProgress ? 'Отправка...' : 'Отправить голоса' }}
          </button>
          
          <button @click="resetVotes" class="btn-secondary">
            Очистить
          </button>
        </div>
        
        <div class="mt-2 text-center text-sm text-hint">
          Проголосовали: {{ votedCount }} из {{ totalVotes }}
        </div>
      </div>
    </div>

    <!-- Нет участников -->
    <div v-else class="card text-center">
      <div class="text-gray-400 mb-2">
        <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
        </svg>
      </div>
      <h3 class="text-lg font-semibold mb-2">Нет участников</h3>
      <p class="text-hint">В текущей сессии нет доступных для голосования участников</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionStore } from '../stores/session'

const router = useRouter()
const sessionStore = useSessionStore()

// Состояние
const votes = ref({})
const comments = ref({})

// Вычисляемые
const votedCount = computed(() => {
  return Object.keys(votes.value).filter(key => votes.value[key] !== undefined).length
})

const totalVotes = computed(() => {
  return sessionStore.votableParticipants.length
})

const progressPercentage = computed(() => {
  if (totalVotes.value === 0) return 0
  return (votedCount.value / totalVotes.value) * 100
})

const canSubmit = computed(() => {
  return votedCount.value === totalVotes.value && totalVotes.value > 0
})

// Методы
const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(word => word[0]).join('').toUpperCase().substring(0, 2)
}

const getScoreLabel = (score) => {
  const labels = {
    0: 'Неудовлетворительно',
    1: 'Очень плохо',
    2: 'Плохо',
    3: 'Ниже среднего',
    4: 'Удовлетворительно',
    5: 'Средне',
    6: 'Выше среднего',
    7: 'Хорошо',
    8: 'Очень хорошо',
    9: 'Отлично',
    10: 'Превосходно'
  }
  return labels[score] || 'Неопределено'
}

const setVote = (userId, score) => {
  votes.value[userId] = score
}

const resetVotes = () => {
  if (window.Telegram?.WebApp) {
    window.Telegram.WebApp.showConfirm('Вы уверены, что хотите очистить все оценки?', (confirmed) => {
      if (confirmed) {
        votes.value = {}
        comments.value = {}
      }
    })
  } else {
    if (confirm('Вы уверены, что хотите очистить все оценки?')) {
      votes.value = {}
      comments.value = {}
    }
  }
}

const submitVotes = async () => {
  if (!canSubmit.value) return
  
  try {
    // Преобразуем голоса в формат API
    const votesArray = Object.entries(votes.value).map(([userId, score]) => ({
      target_id: parseInt(userId),
      score: score,
      comment: comments.value[userId] || null
    }))
    
    await sessionStore.submitVotes(votesArray)
    
    // Переходим на страницу результатов
    router.push('/results')
  } catch (error) {
    console.error('Ошибка отправки голосов:', error)
  }
}

// Жизненный цикл
onMounted(() => {
  // Проверяем, что есть активная сессия
  if (!sessionStore.hasActiveSession) {
    router.push('/')
  }
})
</script>
