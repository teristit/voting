/**
 * Форматирование даты в русском формате
 */
export const formatDate = (dateString) => {
    if (!dateString) return ''
    
    const date = new Date(dateString)
    
    // Проверка валидности даты
    if (isNaN(date.getTime())) return ''
    
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    })
  }
  
  /**
   * Форматирование даты и времени
   */
  export const formatDateTime = (dateString) => {
    if (!dateString) return ''
    
    const date = new Date(dateString)
    
    if (isNaN(date.getTime())) return ''
    
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  /**
   * Расчет оставшихся дней до даты
   */
  export const getDaysRemaining = (endDate) => {
    if (!endDate) return 0
    
    const now = new Date()
    const end = new Date(endDate)
    
    // Устанавливаем время на конец дня для конечной даты
    end.setHours(23, 59, 59, 999)
    
    const diff = end.getTime() - now.getTime()
    
    if (diff <= 0) return 0
    
    return Math.ceil(diff / (1000 * 60 * 60 * 24))
  }
  
  /**
   * Проверка, является ли дата сегодняшним днем
   */
  export const isToday = (dateString) => {
    if (!dateString) return false
    
    const date = new Date(dateString)
    const today = new Date()
    
    return date.toDateString() === today.toDateString()
  }
  
  /**
   * Проверка, является ли дата прошедшей
   */
  export const isPastDate = (dateString) => {
    if (!dateString) return false
    
    const date = new Date(dateString)
    const now = new Date()
    
    return date < now
  }
  
  /**
   * Добавление дней к дате
   */
  export const addDays = (dateString, days) => {
    if (!dateString) return ''
    
    const date = new Date(dateString)
    date.setDate(date.getDate() + days)
    
    return date.toISOString().split('T')[0]
  }
  