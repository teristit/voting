import { apiMethods, handleApiError } from './base.js'

export const sessionsAPI = {
  getCurrent: async () => {
    try {
      const response = await apiMethods.get('/api/v1/sessions/current')
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  create: async (sessionData) => {
    try {
      const response = await apiMethods.post('/api/v1/sessions', sessionData)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  close: async (sessionId, forced = false) => {
    try {
      const response = await apiMethods.post(`/api/v1/sessions/${sessionId}/close`, {
        forced
      })
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  reopen: async (sessionId) => {
    try {
      const response = await apiMethods.post(`/api/v1/sessions/${sessionId}/reopen`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  getAll: async (params = {}) => {
    try {
      const response = await apiMethods.get('/api/v1/admin/sessions', { params })
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  getActive: async () => {
    try {
      const response = await apiMethods.get('/api/v1/admin/sessions/active')
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  getStats: async (sessionId) => {
    try {
      const response = await apiMethods.get(`/api/v1/admin/sessions/${sessionId}/stats`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  getParticipants: async (sessionId) => {
    try {
      const response = await apiMethods.get(`/api/v1/admin/sessions/${sessionId}/participants`)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

  addParticipants: async (sessionId, participants) => {
    try {
      const response = await apiMethods.post(`/api/v1/admin/sessions/${sessionId}/participants`, participants)
      return response
    } catch (error) {
      throw handleApiError(error)
    }
  },

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
  }
}