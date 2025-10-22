// Константы для API
export const API_CONSTANTS = {
    // Роли пользователей
    ROLES: {
      USER: 'user',
      MANAGER: 'manager',
      ADMIN: 'admin'
    },
  
    // Статусы участников
    PARTICIPANT_STATUS: {
      ACTIVE: 'active',
      EXCLUDED: 'excluded',
      VACATION: 'vacation',
      SICK_LEAVE: 'sick_leave'
    },
  
    // Типы действий в логах
    LOG_ACTIONS: {
      USER_LOGIN: 'user_login',
      USER_LOGOUT: 'user_logout',
      VOTE_SUBMIT: 'vote_submit',
      VOTE_UPDATE: 'vote_update',
      VOTE_DELETE: 'vote_delete',
      SESSION_CREATE: 'session_create',
      SESSION_CLOSE: 'session_close',
      SESSION_REOPEN: 'session_reopen',
      USER_CREATE: 'user_create',
      USER_UPDATE: 'user_update',
      USER_DEACTIVATE: 'user_deactivate',
      USER_ACTIVATE: 'user_activate',
      ROLE_CHANGE: 'role_change',
      BONUS_PARAMS_UPDATE: 'bonus_params_update',
      EXPORT_RESULTS: 'export_results',
      SYSTEM_SETTINGS_UPDATE: 'system_settings_update',
      PARTICIPANT_ADDED: 'participant_added',
      PARTICIPANT_UPDATED: 'participant_updated',
      PARTICIPANT_REMOVED: 'participant_removed'
    },
  
    // Форматы экспорта
    EXPORT_FORMATS: {
      XLSX: 'xlsx',
      CSV: 'csv'
    },
  
    // Дни недели для автоматического создания сессий
    WEEK_DAYS: {
      MONDAY: 'monday',
      TUESDAY: 'tuesday',
      WEDNESDAY: 'wednesday',
      THURSDAY: 'thursday',
      FRIDAY: 'friday',
      SATURDAY: 'saturday',
      SUNDAY: 'sunday'
    }
  }
  
  // Преобразование данных для API
  export const transformApiData = {
    // Преобразование данных пользователя для отправки
    userToApi: (userData) => ({
      user_id: userData.userId,
      name: userData.name,
      telegram_username: userData.telegramUsername,
      email: userData.email,
      role: userData.role,
      active: userData.active
    }),
  
    // Преобразование данных сессии для отправки
    sessionToApi: (sessionData) => ({
      start_date: sessionData.startDate,
      end_date: sessionData.endDate,
      active: sessionData.active,
      auto_participants: sessionData.autoParticipants
    }),
  
    // Преобразование голосов для отправки
    votesToApi: (votesData) => ({
      session_id: votesData.sessionId,
      votes: votesData.votes.map(vote => ({
        user_id: vote.userId,
        score: vote.score
      }))
    })
  }