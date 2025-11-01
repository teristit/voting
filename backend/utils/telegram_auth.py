"""
Утилиты для аутентификации Telegram WebApp
"""
import hashlib
import hmac
import json
from urllib.parse import unquote, parse_qsl
from typing import Dict, Optional


def validate_telegram_init_data(init_data: str, bot_token: str) -> Optional[Dict]:
    """
    Проверяет подлинность данных initData от Telegram WebApp
    
    Args:
        init_data: Строка initData от Telegram WebApp
        bot_token: Токен бота Telegram
    
    Returns:
        Dict с данными пользователя или None если проверка не прошла
    """
    try:
        # Парсим init_data
        parsed_data = dict(parse_qsl(init_data))
        
        if 'hash' not in parsed_data:
            return None
            
        received_hash = parsed_data.pop('hash')
        
        # Создаем строку для проверки
        data_check_string = '\n'.join(
            f'{key}={value}' for key, value in sorted(parsed_data.items())
        )
        
        # Создаем secret key
        secret_key = hmac.new(
            "WebAppData".encode(),
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Вычисляем хэш
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Проверяем хэш
        if not hmac.compare_digest(calculated_hash, received_hash):
            return None
            
        # Парсим данные пользователя
        user_data = None
        if 'user' in parsed_data:
            user_data = json.loads(unquote(parsed_data['user']))
            
        return {
            'user': user_data,
            'auth_date': int(parsed_data.get('auth_date', 0)),
            'query_id': parsed_data.get('query_id'),
            'start_param': parsed_data.get('start_param')
        }
        
    except Exception as e:
        print(f"Error validating Telegram init data: {e}")
        return None


def extract_user_from_init_data(validated_data: Dict) -> Optional[Dict]:
    """
    Извлекает информацию о пользователе из проверенных данных
    
    Args:
        validated_data: Проверенные данные от validate_telegram_init_data
    
    Returns:
        Dict с информацией о пользователе
    """
    if not validated_data or 'user' not in validated_data or not validated_data['user']:
        return None
        
    user = validated_data['user']
    
    return {
        'telegram_id': user.get('id'),
        'first_name': user.get('first_name', ''),
        'last_name': user.get('last_name', ''),
        'username': user.get('username', ''),
        'language_code': user.get('language_code', 'en'),
        'is_premium': user.get('is_premium', False)
    }
