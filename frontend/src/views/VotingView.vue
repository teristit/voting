<template>
    <div class="min-h-screen bg-gray-50 py-8">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Информация о сессии -->
        <SessionInfo
          v-if="session"
          :session="session"
          :progress="progress"
          :participants-count="colleagues.length"
          class="mb-8"
        />
  
        <!-- Состояние загрузки -->
        <div v-if="loading && !session" class="flex justify-center items-center py-12">
          <LoadingSpinner size="lg" />
          <span class="ml-3 text-gray-600">Загрузка сессии...</span>
        </div>
  
        <!-- Нет активной сессии -->
        <div v-else-if="!isSessionActive" class="text-center py-12">
          <div class="bg-white rounded-lg border border-gray-200 p-8">
            <div class="text-gray-400 text-6xl mb-4">📅</div>
            <h3 class="text-2xl font-bold text-gray-900 mb-2">
              Нет активных сессий
            </h3>
            <p class="text-gray-600 mb-6">
              В настоящее время нет активных сессий голосования.
            </p>
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
              <p class="text-sm text-blue-700">
                Следующая сессия будет создана администратором. Следите за уведомлениями в Telegram.
              </p>
            </div>
          </div>
        </div>
  
        <!-- Форма голосования -->
        <div v-else>
          <!-- Заголовок формы -->
          <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">
              Оцените работу коллег
            </h2>
            <p class="text-gray-600">
              Поставьте оценки от 0 до 10 для каждого сотрудника. 0 - минимальная оценка, 10 - максимальная.
            </p>
          </div>
  
          <!-- Прогресс голосования -->
          <div class="bg-white rounded-lg border border-gray-200 p-6 mb-6">
            <VotingProgress :progress="progress" />
          </div>
  
          <!-- Список коллег для оценки -->
          <div class="space-y-4 mb-8">
            <ScoreInput
              v-for="colleague in colleagues"
              :key="colleague.user_id"
              :colleague="colleague"
              :model-value="scores[colleague.user_id]"
              @update:model-value="setScore(colleague.user_id, $event)"
            />
          </div>
  
          <!-- Сообщение если нет коллег для оценки -->
          <div v-if="colleagues.length === 0 && !loading" class="text-center py-8">
            <div class="bg-white rounded-lg border border-gray-200 p-8">
              <div class="text-gray-400 text-6xl mb-4">👥</div>
              <h3 class="text-xl font-bold text-gray-900 mb-2">
                Нет коллег для оценки
              </h3>
              <p class="text-gray-600">
                В текущей сессии нет доступных коллег для оценки.
              </p>
            </div>
          </div>
  
          <!-- Действия -->
          <div class="bg-white rounded-lg border border-gray-200 p-6">
            <div class="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
              <!-- Статистика -->
              <div class="text-sm text-gray-600">
                Заполнено: {{ Object.keys(scores).length }}/{{ colleagues.length }}
              </div>
  
              <!-- Кнопки действий -->
              <div class="flex space-x-3">
                <!-- Сброс -->
                <button
                  @click="resetScores"
                  :disabled="Object.keys(scores).length === 0 || submitting"
                  class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Сбросить
                </button>
  
                <!-- Отправка -->
                <button
                  @click="handleSubmit"
                  :disabled="!canSubmit || submitting"
                  :class="[
                    'px-6 py-2 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors',
                    canSubmit && !submitting
                      ? 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  ]"
                >
                  <span v-if="submitting" class="flex items-center">
                    <LoadingSpinner size="sm" class="mr-2" />
                    Отправка...
                  </span>
                  <span v-else>
                    Отправить оценки
                  </span>
                </button>
              </div>
            </div>
          </div>
  
          <!-- Инструкция -->
          <div class="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 class="text-sm font-medium text-blue-800 mb-2">Как оценивать:</h4>
            <ul class="text-sm text-blue-700 space-y-1">
              <li>• <strong>0-3</strong> - требуется значительное улучшение</li>
              <li>• <strong>4-6</strong> - удовлетворительно, есть потенциал роста</li>
              <li>• <strong>7-8</strong> - хорошо, стабильные результаты</li>
              <li>• <strong>9-10</strong> - отлично, выдающиеся достижения</li>
            </ul>
          </div>
        </div>
  
        <!-- Ошибка -->
        <div v-if="error" class="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">
                Ошибка
              </h3>
              <div class="mt-2 text-sm text-red-700">
                <p>{{ error }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { onMounted } from 'vue'
  import { useVoting } from '@/composables/useVoting'
  import SessionInfo from '@/components/voting/SessionInfo.vue'
  import VotingProgress from '@/components/voting/VotingProgress.vue'
  import ScoreInput from '@/components/voting/ScoreInput.vue'
  import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
  
  export default {
    name: 'VotingView',
    components: {
      SessionInfo,
      VotingProgress,
      ScoreInput,
      LoadingSpinner
    },
    setup() {
      const {
        session,
        colleagues,
        scores,
        loading,
        submitting,
        error,
        canSubmit,
        progress,
        isSessionActive,
        setScore,
        resetScores,
        submitVotes,
        initialize
      } = useVoting()
  
      const handleSubmit = async () => {
        try {
          await submitVotes()
          // Успешная отправка обрабатывается в композабле
        } catch (err) {
          // Ошибка обрабатывается в композабле
          console.error('Submit error:', err)
        }
      }
  
      // Инициализация при монтировании компонента
      onMounted(() => {
        initialize()
      })
  
      return {
        // Data
        session,
        colleagues,
        scores,
        loading,
        submitting,
        error,
        
        // Computed
        canSubmit,
        progress,
        isSessionActive,
        
        // Methods
        setScore,
        resetScores,
        handleSubmit
      }
    }
  }
  </script>