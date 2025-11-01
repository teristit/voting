"""
Телеграм-аутентификация без WebApp

Простая проверка по telegram_id пользователя для API вызовов от бота
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger('smart_award')


class TelegramBotAuthentication(BaseAuthentication):
    """
    Простая аутентификация для API вызовов от Telegram бота
    Ищет пользователя по telegram_id в заголовке X-Telegram-User-ID
    """
    
    def authenticate(self, request):
        telegram_id = request.META.get('HTTP_X_TELEGRAM_USER_ID')
        
        if not telegram_id:
            return None
        
        try:
            telegram_id = int(telegram_id)
            user = User.objects.get(telegram_id=telegram_id, is_active=True)
            return (user, None)
        except (ValueError, User.DoesNotExist):
            logger.warning(f"Authentication failed for telegram_id: {telegram_id}")
            return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise AuthenticationFailed('Ошибка аутентификации')
    
    def authenticate_header(self, request):
        return 'X-Telegram-User-ID'