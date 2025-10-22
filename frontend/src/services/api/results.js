import { apiMethods, handleApiError } from './base.js'

export const resultsAPI = {
  /**
   * Получение личных результатов
   */
  getMyResults: async () => {
    try {
      const response = await apiMethods.get('/api/v1/results/me')
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Получение результатов сессии (админ)
   */
  getSessionResults: async (sessionId) => {
    try {
      const response = await apiMethods.get(`/api/v1/results/session/${sessionId}`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Получение статистики сессии (админ)
   */
  getSessionStats: async (sessionId) => {
    try {
      const response = await apiMethods.get(`/api/v1/admin/sessions/${sessionId}/stats`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Сравнительная аналитика сессий (админ)
   */
  getSessionsComparison: async (sessionIds) => {
    try {
      const response = await apiMethods.get('/api/v1/admin/analytics/sessions/comparison', {
        params: { session_ids: sessionIds.join(',') }
      })
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  }
}