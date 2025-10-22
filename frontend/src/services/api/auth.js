import { apiMethods, handleApiError } from './base.js'

export const authAPI = {
  telegramAuth: async (initData) => {
    try {
      const response = await apiMethods.post('/api/v1/auth/telegram', {
        init_data: initData
      })
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  logout: async () => {
    try {
      const response = await apiMethods.post('/api/v1/auth/logout')
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  refreshToken: async () => {
    try {
      const response = await apiMethods.post('/api/v1/auth/refresh')
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  validateToken: async () => {
    try {
      const response = await apiMethods.get('/api/v1/auth/validate')
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  }
}