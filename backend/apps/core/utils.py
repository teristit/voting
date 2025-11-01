"""
Вспомогательные утилиты для Smart Award
"""

import logging
from typing import Optional, Dict, Any
from django.conf import settings
from django.utils import timezone
import json


def get_logger(name: str) -> logging.Logger:
    """
    Получает настроенный логгер
    """
    return logging.getLogger(name)


def get_client_ip(request) -> str:
    """
    Получает IP адрес клиента из запроса
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def safe_json_loads(data: str) -> Optional[Dict]:
    """
    Безопасно парсит JSON строку
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return None


def format_bonus_amount(amount: float) -> str:
    """
    Форматирует сумму премии для отображения
    """
    return f"{amount:.2f} ₽"


def is_valid_score(score: int) -> bool:
    """
    Проверяет валидность оценки
    """
    min_score = settings.SMART_AWARD['VOTE_SCALE_MIN']
    max_score = settings.SMART_AWARD['VOTE_SCALE_MAX']
    return min_score <= score <= max_score


def get_current_week_dates():
    """
    Получает даты начала и конца текущей недели
    """
    now = timezone.now().date()
    start_of_week = now - timezone.timedelta(days=now.weekday())
    end_of_week = start_of_week + timezone.timedelta(days=6)
    return start_of_week, end_of_week


class SmartAwardError(Exception):
    """
    Базовое исключение для Smart Award
    """
    pass


class VotingError(SmartAwardError):
    """
    Ошибки голосования
    """
    pass


class SessionError(SmartAwardError):
    """
    Ошибки сессий голосования
    """
    pass