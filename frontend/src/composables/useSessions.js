import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { sessionsAPI } from '@/services/api'
import { formatDate, getDaysRemaining } from '@/utils/date'

export const useSessions = () => {
  const authStore = useAuthStore()
  
  const currentSession = ref(null)
  const sessions = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Получение текущей активной сессии
  const fetchCurrentSession = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await sessionsAPI.getCurrent()
      currentSession.value = response.data
      return currentSession.value
    } catch (err) {
      error.value = err.message || 'Не удалось загрузить текущую сессию'
      console.error('Failed to fetch current session:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Получение списка всех сессий (для админа)
  const fetchSessions = async (params = {}) => {
    if (!authStore.isAdmin) return
    
    loading.value = true
    error.value = null
    
    try {
      const response = await sessionsAPI.getAll(params)
      sessions.value = response.data.sessions || []
      return sessions.value
    } catch (err) {
      error.value = err.message || 'Не удалось загрузить сессии'
      console.error('Failed to fetch sessions:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Проверка, активна ли текущая сессия
  const isSessionActive = computed(() => {
    return currentSession.value?.active === true
  })

  // Оставшееся время до конца сессии
  const timeRemaining = computed(() => {
    if (!currentSession.value?.end_date) return null
    
    const days = getDaysRemaining(currentSession.value.end_date)
    if (days <= 0) return 'завершена'
    if (days === 1) return '1 день'
    if (days < 7) return `${days} дня`
    return `${Math.ceil(days / 7)} недель`
  })

  // Форматированная дата сессии
  const formattedSessionDate = computed(() => {
    if (!currentSession.value) return ''
    return `${formatDate(currentSession.value.start_date)} - ${formatDate(currentSession.value.end_date)}`
  })

  return {
    // Data
    currentSession,
    sessions,
    loading,
    error,
    
    // Computed
    isSessionActive,
    timeRemaining,
    formattedSessionDate,
    
    // Methods
    fetchCurrentSession,
    fetchSessions,
    
    // Утилиты
    refresh: fetchCurrentSession
  }
}