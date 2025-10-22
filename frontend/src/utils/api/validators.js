// Валидаторы для данных API
export const apiValidators = {
    // Валидация оценки
    validateScore: (score) => {
      const numScore = Number(score)
      return !isNaN(numScore) && numScore >= 0 && numScore <= 10
    },
  
    // Валидация даты
    validateDate: (dateString) => {
      const date = new Date(dateString)
      return date instanceof Date && !isNaN(date)
    },
  
    // Валидация email
    validateEmail: (email) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    },
  
    // Валидация параметров премии
    validateBonusParams: (params) => {
      const { average_weekly_revenue, participation_multiplier, total_weekly_bonus } = params
      
      return (
        typeof average_weekly_revenue === 'number' && average_weekly_revenue >= 0 &&
        typeof participation_multiplier === 'number' && 
        participation_multiplier >= 0 && participation_multiplier <= 1 &&
        typeof total_weekly_bonus === 'number' && total_weekly_bonus >= 0
      )
    },
  
    // Валидация данных пользователя
    validateUserData: (userData) => {
      const { user_id, name, role } = userData
      
      return (
        typeof user_id === 'number' &&
        typeof name === 'string' && name.trim().length > 0 &&
        ['user', 'manager', 'admin'].includes(role)
      )
    }
  }
  
  // Генерация сообщений об ошибках валидации
  export const validationMessages = {
    INVALID_SCORE: 'Оценка должна быть числом от 0 до 10',
    INVALID_DATE: 'Некорректный формат даты',
    INVALID_EMAIL: 'Некорректный формат email',
    INVALID_BONUS_PARAMS: 'Некорректные параметры премии',
    INVALID_USER_DATA: 'Некорректные данные пользователя',
    REQUIRED_FIELD: 'Обязательное поле'
  }