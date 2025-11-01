import axios from 'axios'

// Конфигурация API клиента
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 секунд
  headers: {
    'Content-Type': 'application/json',
  },
})

// Интерцептор запросов
apiClient.interceptors.request.use(
  (config) => {
    // Добавляем токен аутентификации если он есть
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Логируем запросы в режиме разработки
    if (import.meta.env.DEV) {
      console.log(`→ ${config.method?.toUpperCase()} ${config.url}`, config.data || config.params)
    }
    
    return config
  },
  (error) => {
    console.error('Ошибка запроса:', error)
    return Promise.reject(error)
  }
)

// Интерцептор ответов
apiClient.interceptors.response.use(
  (response) => {
    // Логируем ответы в режиме разработки
    if (import.meta.env.DEV) {
      console.log(`← ${response.status} ${response.config.url}`, response.data)
    }
    
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // Обработка ошибки 401 (неавторизован)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        // Пробуем обновить токен
        const refreshResponse = await apiClient.post('/auth/refresh')
        
        if (refreshResponse.data.status === 'success') {
          const newToken = refreshResponse.data.token
          localStorage.setItem('auth_token', newToken)
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`
          
          // Повторяем оригинальный запрос
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // Обновление токена не удалось
        console.error('Ошибка обновления токена:', refreshError)
        
        // Очищаем данные аутентификации
        localStorage.removeItem('auth_token')
        delete apiClient.defaults.headers.common['Authorization']
        
        // Перезагружаем страницу для повторной аутентификации
        if (typeof window !== 'undefined') {
          window.location.reload()
        }
      }
    }
    
    // Логирование ошибок
    if (import.meta.env.DEV) {
      console.error(
        `← ${error.response?.status || 'Network Error'} ${originalRequest?.url}`,
        error.response?.data || error.message
      )
    }
    
    // Обработка сетевых ошибок
    if (!error.response) {
      // Ошибка сети или тайм-аут
      const networkError = new Error('Ошибка сети. Проверьте подключение к интернету')
      networkError.isNetworkError = true
      return Promise.reject(networkError)
    }
    
    return Promise.reject(error)
  }
)

// Вспомогательные функции для работы с API
export const api = {
  // Аутентификация
  auth: {
    telegram: (initData) => apiClient.post('/auth/telegram', { init_data: initData }),
    logout: () => apiClient.post('/auth/logout'),
    refresh: () => apiClient.post('/auth/refresh'),
  },
  
  // Пользователи
  users: {
    me: () => apiClient.get('/users/me'),
    profile: () => apiClient.get('/users/profile'),
    updateProfile: (data) => apiClient.put('/users/profile', data),
  },
  
  // Сессии
  sessions: {
    current: () => apiClient.get('/sessions/current'),
    list: (params) => apiClient.get('/sessions', { params }),
    get: (id) => apiClient.get(`/sessions/${id}`),
    participants: (id) => apiClient.get(`/sessions/${id}/participants`),
    bonusParams: (id) => apiClient.get(`/sessions/${id}/bonus-params`),
    setBonusParams: (id, data) => apiClient.post(`/sessions/${id}/bonus-params`, data),
  },
  
  // Голосование
  votes: {
    submit: (data) => apiClient.post('/votes', data),
    my: () => apiClient.get('/votes/my'),
    update: (voteId, data) => apiClient.put(`/votes/${voteId}`, data),
  },
  
  // Результаты
  results: {
    me: () => apiClient.get('/results/me'),
    session: (sessionId) => apiClient.get(`/results/session/${sessionId}`),
    calculate: (sessionId) => apiClient.post(`/results/session/${sessionId}/calculate`),
  },
  
  // Администрирование
  admin: {
    sessions: {
      create: (data) => apiClient.post('/admin/sessions', data),
      update: (id, data) => apiClient.put(`/admin/sessions/${id}`, data),
      close: (id) => apiClient.post(`/admin/sessions/${id}/close`),
      reopen: (id) => apiClient.post(`/admin/sessions/${id}/reopen`),
      delete: (id) => apiClient.delete(`/admin/sessions/${id}`),
    },
    participants: {
      add: (sessionId, data) => apiClient.post(`/admin/sessions/${sessionId}/participants`, data),
      update: (sessionId, participantId, data) => apiClient.put(`/admin/sessions/${sessionId}/participants/${participantId}`, data),
      remove: (sessionId, participantId) => apiClient.delete(`/admin/sessions/${sessionId}/participants/${participantId}`),
      bulkAdd: (sessionId, data) => apiClient.post(`/admin/sessions/${sessionId}/participants/bulk`, data),
    },
    votes: {
      list: (sessionId, params) => apiClient.get(`/admin/sessions/${sessionId}/votes`, { params }),
      update: (voteId, data) => apiClient.put(`/admin/votes/${voteId}`, data),
      delete: (voteId) => apiClient.delete(`/admin/votes/${voteId}`),
    },
    export: {
      sessionResults: (sessionId, format = 'xlsx') => 
        apiClient.get(`/admin/export/session/${sessionId}/results`, { 
          params: { format },
          responseType: 'blob'
        }),
      sessionParticipants: (sessionId, format = 'xlsx') => 
        apiClient.get(`/admin/export/session/${sessionId}/participants`, { 
          params: { format },
          responseType: 'blob'
        }),
      payments: (sessionId, format = 'csv') => 
        apiClient.get(`/admin/export/session/${sessionId}/payments`, { 
          params: { format },
          responseType: 'blob'
        }),
    },
    settings: {
      get: () => apiClient.get('/admin/settings'),
      update: (data) => apiClient.put('/admin/settings', data),
    },
    audit: {
      list: (params) => apiClient.get('/admin/audit', { params }),
      export: (params) => apiClient.get('/admin/audit/export', { params, responseType: 'blob' }),
    },
  },
}

export default api
