import { apiMethods, handleApiError } from './base.js'

export const settingsAPI = {
  /**
   * Получение системных настроек
   */
  getSettings: async () => {
    try {
      const response = await apiMethods.get('/api/v1/admin/settings')
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Обновление системных настроек (админ)
   */
  updateSettings: async (settings) => {
    try {
      const response = await apiMethods.put('/api/v1/admin/settings', settings)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Настройка автоматического создания сессий (админ)
   */
  setAutoSessionSettings: async (autoSettings) => {
    try {
      const response = await apiMethods.put('/api/v1/admin/settings', {
        auto_create_sessions: autoSettings.autoCreate,
        session_start_day: autoSettings.startDay,
        session_duration_days: autoSettings.durationDays,
        advance_creation_days: autoSettings.advanceDays,
        auto_add_participants: autoSettings.autoAddParticipants
      })
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  }
}