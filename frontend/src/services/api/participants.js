import { apiMethods, handleApiError } from './base.js'

export const participantsAPI = {
  /**
   * Получение участников сессии (админ)
   */
  getSessionParticipants: async (sessionId) => {
    try {
      const response = await apiMethods.get(`/api/v1/admin/sessions/${sessionId}/participants`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Добавление участников в сессию (админ)
   */
  addParticipants: async (sessionId, participants) => {
    try {
      const response = await apiMethods.post(`/api/v1/admin/sessions/${sessionId}/participants`, participants)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Обновление прав участника (админ)
   */
  updateParticipant: async (sessionId, participantId, data) => {
    try {
      const response = await apiMethods.patch(
        `/api/v1/admin/sessions/${sessionId}/participants/${participantId}`,
        data
      )
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Удаление участника из сессии (админ)
   */
  removeParticipant: async (sessionId, participantId) => {
    try {
      const response = await apiMethods.delete(
        `/api/v1/admin/sessions/${sessionId}/participants/${participantId}`
      )
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Массовое изменение статуса участников (админ)
   */
  bulkUpdateParticipants: async (sessionId, updates) => {
    try {
      const response = await apiMethods.post(
        `/api/v1/admin/sessions/${sessionId}/participants/bulk-status`,
        updates
      )
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Импорт участников из CSV (админ)
   */
  importParticipants: async (sessionId, file) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await apiMethods.post(
        `/api/v1/admin/sessions/${sessionId}/participants/import`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Автоматическое добавление активных пользователей (админ)
   */
  addActiveUsers: async (sessionId) => {
    try {
      const response = await apiMethods.post(`/api/v1/admin/sessions/${sessionId}/participants/add-active`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Отправка напоминания не проголосовавшим (админ)
   */
  sendReminder: async (sessionId) => {
    try {
      const response = await apiMethods.post(`/api/v1/admin/sessions/${sessionId}/remind`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  }
}
