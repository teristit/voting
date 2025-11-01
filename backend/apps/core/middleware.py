"""
Middleware для системы Smart Award
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger('smart_award')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Логирование HTTP запросов
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        
        # Логируем только API запросы и важные действия
        if request.path.startswith('/api/') or request.path.startswith('/telegram/'):
            logger.info(f"{request.method} {request.path} from {request.META.get('REMOTE_ADDR')}")
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Логируем медленные запросы
            if duration > 1.0:  # Более секунды
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {duration:.2f}s - Status: {response.status_code}"
                )
        
        return response