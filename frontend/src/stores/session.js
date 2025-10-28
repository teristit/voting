import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '../services/api'

export const useSessionStore = defineStore('session', () => {
  // Состояние
  const currentSession = ref(null)
  const participants = ref([])
  const myVotes = ref([])
  const sessionResults = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  const votingInProgress = ref(false)

  // Вычисляемые свойства
  const hasActiveSession = computed(() => {
    return currentSession.value && currentSession.value.active
  })

  const canVote = computed(() => {
    return hasActiveSession.value && 
           currentSession.value.can_vote &&
           !hasVoted.value
  })

  const hasVoted = computed(() => {
    return myVotes.value && myVotes.value.length > 0
  })

  const sessionDaysLeft = computed(() => {
    if (!currentSession.value?.end_date) return 0
    
    const endDate = new Date(currentSession.value.end_date)
    const now = new Date()
    const diffTime = endDate - now
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    return Math.max(0, diffDays)
  })

  const votableParticipants = computed(() => {
    return participants.value.filter(p => 
      p.can_receive_votes && 
      p.status === 'active' &&
      p.user_id !== currentSession.value?.current_user_id
    )
  })

  // Методы
  const loadCurrentSession = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.get('/sessions/current')
      
      if (response.data.status === 'success') {
        currentSession.value = response.data.session
        
        if (hasActiveSession.value) {
          await Promise.all([
            loadSessionParticipants(),
            loadMyVotes()
          ])
        }
      }
    } catch (err) {
      console.error('Ошибка загрузки текущей сессии:', err)
      error.value = 'Ошибка загрузки сессии'
    } finally {
      isLoading.value = false
    }
  }

  const loadSessionParticipants = async () => {
    if (!currentSession.value?.session_id) return

    try {
      const response = await apiClient.get(`/sessions/${currentSession.value.session_id}/participants`)
      
      if (response.data.status === 'success') {
        participants.value = response.data.participants
      }
    } catch (err) {
      console.error('Ошибка загрузки участников:', err)
    }
  }

  const loadMyVotes = async () => {
    if (!currentSession.value?.session_id) return

    try {
      const response = await apiClient.get('/results/me')
      
      if (response.data.status === 'success') {
        myVotes.value = response.data.votes || []
      }
    } catch (err) {
      console.error('Ошибка загрузки моих голосов:', err)
    }
  }

  const submitVotes = async (votes) => {
    if (!currentSession.value?.session_id || !votes || votes.length === 0) {
      throw new Error('Некорректные данные для голосования')
    }

    votingInProgress.value = true
    error.value = null

    try {
      const response = await apiClient.post('/votes', {
        session_id: currentSession.value.session_id,
        votes: votes
      })

      if (response.data.status === 'success') {
        // Обновляем мои голоса
        myVotes.value = votes
        
        // Показываем успешное уведомление
        if (window.Telegram?.WebApp) {
          window.Telegram.WebApp.showAlert('Голоса успешно отправлены!')
        }
        
        return true
      } else {
        throw new Error(response.data.message || 'Ошибка отправки голосов')
      }
    } catch (err) {
      console.error('Ошибка отправки голосов:', err)
      
      let errorMessage = 'Ошибка отправки голосов'
      
      if (err.response?.data?.message) {
        errorMessage = err.response.data.message
      } else if (err.response?.status === 409) {
        errorMessage = 'Вы уже проголосовали в этой сессии'
      } else if (err.response?.status === 422) {
        errorMessage = 'Некорректные данные голосов'
      }
      
      error.value = errorMessage
      
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.showAlert(errorMessage)
      }
      
      throw new Error(errorMessage)
    } finally {
      votingInProgress.value = false
    }
  }

  const loadSessionResults = async (sessionId = null) => {
    const targetSessionId = sessionId || currentSession.value?.session_id
    if (!targetSessionId) return

    try {
      const response = await apiClient.get(`/results/session/${targetSessionId}`)
      
      if (response.data.status === 'success') {
        sessionResults.value = response.data.results
        return response.data.results
      }
    } catch (err) {
      console.error('Ошибка загрузки результатов:', err)
    }
    
    return null
  }

  const loadBonusParameters = async (sessionId = null) => {
    const targetSessionId = sessionId || currentSession.value?.session_id
    if (!targetSessionId) return null

    try {
      const response = await apiClient.get(`/sessions/${targetSessionId}/bonus-params`)
      
      if (response.data.status === 'success') {
        return response.data.bonus_parameters
      }
    } catch (err) {
      console.error('Ошибка загрузки параметров бонусов:', err)
    }
    
    return null
  }

  const refreshSession = async () => {
    await loadCurrentSession()
  }

  const clearSession = () => {
    currentSession.value = null
    participants.value = []
    myVotes.value = []
    sessionResults.value = null
    error.value = null
  }

  const clearError = () => {
    error.value = null
  }

  const getParticipantById = (userId) => {
    return participants.value.find(p => p.user_id === userId)
  }

  const getVoteForParticipant = (userId) => {
    return myVotes.value.find(v => v.target_id === userId)
  }

  return {
    // Состояние
    currentSession,
    participants,
    myVotes,
    sessionResults,
    isLoading,
    error,
    votingInProgress,
    
    // Вычисляемые
    hasActiveSession,
    canVote,
    hasVoted,
    sessionDaysLeft,
    votableParticipants,
    
    // Методы
    loadCurrentSession,
    loadSessionParticipants,
    loadMyVotes,
    submitVotes,
    loadSessionResults,
    loadBonusParameters,
    refreshSession,
    clearSession,
    clearError,
    getParticipantById,
    getVoteForParticipant
  }
})
