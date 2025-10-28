import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient } from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  // Состояние
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const isLoading = ref(false)
  const error = ref(null)
  const initialized = ref(false)

  // Вычисляемые свойства
  const isAuthenticated = computed(() => {
    return !!(user.value && token.value)
  })

  const isAdmin = computed(() => {
    return user.value?.role === 'admin'
  })

  // Методы
  const setToken = (newToken) => {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('auth_token', newToken)
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
    } else {
      localStorage.removeItem('auth_token')
      delete apiClient.defaults.headers.common['Authorization']
    }
  }

  const setUser = (userData) => {
    user.value = userData
  }

  const clearAuth = () => {
    user.value = null
    setToken(null)
    error.value = null
  }

  const init = async () => {
    if (initialized.value) return
    
    isLoading.value = true
    error.value = null

    try {
      // Проверяем, есть ли сохраненный токен
      if (token.value) {
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
        
        try {
          // Проверяем валидность токена
          const response = await apiClient.get('/users/me')
          setUser(response.data.user)
        } catch (error) {
          // Токен невалиден, очищаем
          clearAuth()
        }
      }

      // Пробуем аутентифицироваться через Telegram
      if (!isAuthenticated.value && window.Telegram?.WebApp?.initData) {
        await login()
      }
    } catch (err) {
      console.error('Ошибка инициализации:', err)
      error.value = 'Ошибка инициализации приложения'
    } finally {
      isLoading.value = false
      initialized.value = true
    }
  }

  const login = async () => {
    if (!window.Telegram?.WebApp?.initData) {
      error.value = 'Приложение должно быть запущено в Telegram'
      return false
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.post('/auth/telegram', {
        init_data: window.Telegram.WebApp.initData
      })

      if (response.data.status === 'success') {
        setToken(response.data.token)
        setUser(response.data.user)
        return true
      } else {
        throw new Error(response.data.message || 'Ошибка аутентификации')
      }
    } catch (err) {
      console.error('Ошибка входа:', err)
      
      let errorMessage = 'Ошибка входа в систему'
      
      if (err.response?.data?.message) {
        errorMessage = err.response.data.message
      } else if (err.response?.status === 401) {
        errorMessage = 'Неверные данные аутентификации'
      } else if (err.response?.status === 403) {
        errorMessage = 'Доступ запрещен. Обратитесь к администратору'
      } else if (!navigator.onLine) {
        errorMessage = 'Отсутствует подключение к интернету'
      }
      
      error.value = errorMessage
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    isLoading.value = true
    
    try {
      // Уведомляем сервер о выходе
      if (token.value) {
        await apiClient.post('/auth/logout')
      }
    } catch (err) {
      console.error('Ошибка при выходе:', err)
    } finally {
      clearAuth()
      isLoading.value = false
      
      // Перезагружаем страницу для очистки состояния
      window.location.reload()
    }
  }

  const refreshToken = async () => {
    if (!token.value) return false
    
    try {
      const response = await apiClient.post('/auth/refresh')
      
      if (response.data.status === 'success') {
        setToken(response.data.token)
        return true
      }
    } catch (err) {
      console.error('Ошибка обновления токена:', err)
      clearAuth()
    }
    
    return false
  }

  const clearError = () => {
    error.value = null
  }

  const updateUser = (userData) => {
    if (user.value) {
      user.value = { ...user.value, ...userData }
    }
  }

  return {
    // Состояние
    user,
    token,
    isLoading,
    error,
    initialized,
    
    // Вычисляемые
    isAuthenticated,
    isAdmin,
    
    // Методы
    init,
    login,
    logout,
    refreshToken,
    clearError,
    updateUser,
    setUser,
    setToken,
    clearAuth
  }
})
