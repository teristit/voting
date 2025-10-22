import { downloadFile, handleApiError } from './base.js'

export const exportAPI = {
  /**
   * Экспорт результатов сессии
   */
  exportSession: async (sessionId, format = 'xlsx') => {
    try {
      const filename = `session_${sessionId}_results.${format}`
      await downloadFile(`/api/v1/admin/export/session/${sessionId}`, filename, { format })
      return { success: true, filename }
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Экспорт данных для бухгалтерии
   */
  exportPayments: async (sessionId, format = 'csv') => {
    try {
      const filename = `session_${sessionId}_payments.${format}`
      await downloadFile(`/api/v1/admin/export/session/${sessionId}/payments`, filename, { format })
      return { success: true, filename }
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Полный экспорт данных за период (админ)
   */
  exportFullData: async (dateFrom, dateTo, format = 'xlsx') => {
    try {
      const filename = `full_export_${dateFrom}_to_${dateTo}.${format}`
      await downloadFile('/api/v1/admin/export/full', filename, {
        date_from: dateFrom,
        date_to: dateTo,
        format
      })
      return { success: true, filename }
    } catch (error) {
      throw handleApiError(error)
    }
  },

  /**
   * Экспорт логов (админ)
   */
  exportLogs: async (params = {}) => {
    try {
      const filename = `logs_export_${new Date().toISOString().split('T')[0]}.csv`
      await downloadFile('/api/v1/admin/logs/export', filename, params)
      return { success: true, filename }
    } catch (error) {
      throw handleApiError(error)
    }
  }
}