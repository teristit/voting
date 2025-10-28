import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useSessions } from './useSessions'
import { votesAPI } from '@/services/api'
import { inject } from 'vue'

export const useVoting = () => {
  const authStore = useAuthStore()
  const showNotification = inject('showNotification')
  
  const {
    currentSession,
    loading: sessionLoading,
    error: sessionError,
    fetchCurrentSession
  } = useSessions()

  // Состояние голосования
  const colleagues = ref([])
  const scores = ref({})
  const submitting = ref(false)
  const voteLoading = ref(false)
  const voteError = ref(null)

  // Получение списка коллег для голосования
  const fetchColleagues = async () => {
    if (!currentSession.value?.session_id) return
    
    voteLoading.value = true
    voteError.value = null
    
    try {
      // В реальном приложении здесь будет запрос к API
      // Пока используем моковые данные
      const response = await sessionsAPI.getParticipants(currentSession.value.session_id)
      colleagues.value = response.data.participants
        .filter(participant => 
          participant.status === 'active' && 
          participant.user_id !== authStore.user?.user_id
        )
        .map(participant => ({
          user_id: participant.user_id,
          name: participant.name,
          can_vote: participant.can_vote,
          can_receive_votes: participant.can_receive_votes
        }))
    } catch (err) {
      voteError.value = err.message || 'Не удалось загрузить список коллег'
      console.error('Failed to fetch colleagues:', err)
    } finally {
      voteLoading.value = false
    }
  }

  // Установка оценки для коллеги
  const setScore = (userId, score) => {
    if (score < 0 || score > 10) {
      console.warn('Score must be between 0 and 10')
      return
    }
    
    scores.value = {
      ...scores.value,
      [userId]: score
    }
  }

  // Сброс всех оценок
  const resetScores = () => {
    scores.value = {}
  }

  // Отправка голосов на сервер
  const submitVotes = async () => {
    if (!canSubmit.value) {
      throw new Error('Не все оценки заполнены')
    }

    submitting.value = true
    voteError.value = null

    try {
      const votes = Object.entries(scores.value)
        .filter(([userId, score]) => score !== null && score !== undefined)
        .map(([userId, score]) => ({
          user_id: parseInt(userId),
          score: score
        }))

      const voteData = {
        session_id: currentSession.value.session_id,
        votes: votes
      }

      await votesAPI.submit(voteData)
      
      // Очищаем оценки после успешной отправки
      resetScores()
      
      // Показываем уведомление об успехе
      if (showNotification) {
        showNotification({
          type: 'success',
          title: 'Голосование завершено',
          message: 'Ваши оценки успешно отправлены!',
          duration: 5000
        })
      }
      
      return true
    } catch (err) {
      voteError.value = err.message || 'Ошибка при отправке оценок'
      
      if (showNotification) {
        showNotification({
          type: 'error',
          title: 'Ошибка',
          message: voteError.value,
          duration: 5000
        })
      }
      
      console.error('Failed to submit votes:', err)
      throw err
    } finally {
      submitting.value = false
    }
  }

  // Вычисляемые свойства
  const canSubmit = computed(() => {
    if (!currentSession.value?.active) return false
    if (colleagues.value.length === 0) return false
    
    // Проверяем, что все обязательные оценки заполнены
    const requiredColleagues = colleagues.value.filter(colleague => colleague.can_receive_votes)
    const filledScores = Object.keys(scores.value).length
    
    return filledScores === requiredColleagues.length
  })

  const progress = computed(() => {
    if (colleagues.value.length === 0) return 0
    
    const requiredColleagues = colleagues.value.filter(colleague => colleague.can_receive_votes)
    const filledScores = Object.keys(scores.value).length
    
    return Math.round((filledScores / requiredColleagues.length) * 100)
  })

  const totalLoading = computed(() => sessionLoading.value || voteLoading.value)

  // Автоматическая загрузка коллег при изменении сессии
  watch(
    () => currentSession.value,
    (newSession) => {
      if (newSession?.active) {
        fetchColleagues()
      }
    },
    { immediate: true }
  )

  // Инициализация - загружаем текущую сессию
  const initialize = async () => {
    await fetchCurrentSession()
  }

  return {
    // Data
    session: currentSession,
    colleagues,
    scores,
    loading: totalLoading,
    submitting,
    error: computed(() => sessionError.value || voteError.value),
    
    // Computed
    canSubmit,
    progress,
    isSessionActive: computed(() => currentSession.value?.active),
    
    // Methods
    setScore,
    resetScores,
    submitVotes,
    initialize,
    refresh: fetchCurrentSession
  }
}