import { apiMethods, handleApiError } from './base.js'

export const votesAPI = {
  /**
   * Отправка голосов
   */
  submit: async (voteData) => {
    try {
      const response = await apiMethods.post('/api/v1/votes', voteData)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Получение всех голосов сессии (админ)
   */
  getSessionVotes: async (sessionId) => {
    try {
      const response = await apiMethods.get(`/api/v1/admin/sessions/${sessionId}/votes`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Изменение оценки (админ)
   */
  updateVote: async (voteId, newScore, reason = '') => {
    try {
      const response = await apiMethods.patch(`/api/v1/admin/votes/${voteId}`, {
        new_score: newScore,
        reason
      })
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Удаление голоса (админ)
   */
  deleteVote: async (voteId) => {
    try {
      const response = await apiMethods.delete(`/api/v1/admin/votes/${voteId}`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Принудительный перерасчет результатов сессии (админ)
   */
  recalculateSession: async (sessionId) => {
    try {
      const response = await apiMethods.post(`/api/v1/admin/sessions/${sessionId}/recalculate`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  }
}