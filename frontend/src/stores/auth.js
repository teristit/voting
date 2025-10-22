import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/services/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  const loading = ref(false)
  const error = ref(null)
  
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isManager = computed(() => user.value?.role === 'manager')
  const isUser = computed(() => user.value?.role === 'user')
  
  const initAuth = async () => {
    loading.value = true
    error.value = null
    
    try {
      const initData = window.Telegram?.WebApp?.initData
      if (!initData) {
        throw new Error('Telegram WebApp data not found')
      }
      
      const response = await authAPI.telegramAuth(initData)
      token.value = response.data.token
      user.value = response.data.user
      
      localStorage.setItem('auth_token', token.value)
      localStorage.setItem('user', JSON.stringify(user.value))
      
      return response.data
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      console.error('Auth error:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const logout = () => {
    user.value = null
    token.value = null
    error.value = null
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
  
  const updateUser = (userData) => {
    if (user.value) {
      user.value = { ...user.value, ...userData }
      localStorage.setItem('user', JSON.stringify(user.value))
    }
  }
  
  const clearError = () => {
    error.value = null
  }
  
  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    isManager,
    isUser,
    initAuth,
    logout,
    restoreSession,
    updateUser,
    clearError
  }
})