export const USER_ROLES = {
  USER: 'user',
  MANAGER: 'manager',
  ADMIN: 'admin'
}

export const ROLE_PERMISSIONS = {
  [USER_ROLES.USER]: ['vote:submit', 'results:view'],
  [USER_ROLES.MANAGER]: ['vote:submit', 'results:view', 'users:read', 'exports:read'],
  [USER_ROLES.ADMIN]: ['*']
}

export const ROLE_LABELS = {
  [USER_ROLES.USER]: 'РЎРѕС‚СЂСѓРґРЅРёРє',
  [USER_ROLES.MANAGER]: 'Р СѓРєРѕРІРѕРґРёС‚РµР»СЊ',
  [USER_ROLES.ADMIN]: 'РђРґРјРёРЅРёСЃС‚СЂР°С‚РѕСЂ'
}
