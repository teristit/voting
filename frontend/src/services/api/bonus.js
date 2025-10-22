import { apiMethods, handleApiError } from './base.js'

export const bonusAPI = {
  /**
   * Установка параметров премии для сессии (админ)
   */
  setBonusParams: async (sessionId, params) => {
    try {
      const response = await apiMethods.post(`/api/v1/admin/sessions/${sessionId}/bonus-params`, params)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Получение параметров премии для сессии
   */
  getBonusParams: async (sessionId) => {
    try {
      const response = await apiMethods.get(`/api/v1/admin/sessions/${sessionId}/bonus-params`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Создание шаблона параметров премии (админ)
   */
  createBonusTemplate: async (templateData) => {
    try {
      const response = await apiMethods.post('/api/v1/admin/bonus-templates', templateData)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Получение списка шаблонов (админ)
   */
  getBonusTemplates: async () => {
    try {
      const response = await apiMethods.get('/api/v1/admin/bonus-templates')
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Применение шаблона к сессии (админ)
   */
  applyBonusTemplate: async (sessionId, templateId) => {
    try {
      const response = await apiMethods.post(`/api/v1/admin/sessions/${sessionId}/apply-template/${templateId}`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  }
}