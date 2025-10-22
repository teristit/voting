import { apiMethods, handleApiError } from './base.js'

export const logsAPI = {
  /**
   * Получение журнала действий (админ)
   */
  getLogs: async (params = {}) => {
    try {
      const response = await apiMethods.get('/api/v1/admin/logs', { params })
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Получение логов с пагинацией (админ)
   */
  getLogsPaginated: async (page = 1, limit = 50, filters = {}) => {
    try {
      const response = await apiMethods.get('/api/v1/admin/logs', {
        params: { page, limit, ...filters }
      })
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Получение типов действий для фильтрации (админ)
   */
  getLogActions: async () => {
    try {
      const response = await apiMethods.get('/api/v1/admin/logs/actions')
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  }
}