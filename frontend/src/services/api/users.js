import { apiMethods, handleApiError } from './base.js'

export const usersAPI = {
  /**
   * Получение списка пользователей (админ)
   */
  getUsers: async (params = {}) => {
    try {
      const response = await apiMethods.get('/api/v1/admin/users', { params })
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Создание пользователя (админ)
   */
  createUser: async (userData) => {
    try {
      const response = await apiMethods.post('/api/v1/admin/users', userData)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Обновление пользователя (админ)
   */
  updateUser: async (userId, userData) => {
    try {
      const response = await apiMethods.put(`/api/v1/admin/users/${userId}`, userData)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Массовое добавление пользователей (админ)
   */
  bulkCreateUsers: async (users) => {
    try {
      const response = await apiMethods.post('/api/v1/admin/users/bulk', { users })
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Деактивация пользователя (админ)
   */
  deactivateUser: async (userId) => {
    try {
      const response = await apiMethods.post(`/api/v1/admin/users/${userId}/deactivate`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Активация пользователя (админ)
   */
  activateUser: async (userId) => {
    try {
      const response = await apiMethods.post(`/api/v1/admin/users/${userId}/activate`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Изменение роли пользователя (админ)
   */
  updateUserRole: async (userId, roleData) => {
    try {
      const response = await apiMethods.put(`/api/v1/admin/users/${userId}/role`, roleData)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Поиск пользователей (админ)
   */
  searchUsers: async (query) => {
    try {
      const response = await apiMethods.get('/api/v1/admin/users/search', {
        params: { query }
      })
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Статистика пользователей (админ)
   */
  getUsersStats: async () => {
    try {
      const response = await apiMethods.get('/api/v1/admin/users/stats')
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  }
}