"""
Утилиты для системы Умная Премия
"""

from .telegram_auth import validate_telegram_init_data, extract_user_from_init_data

__all__ = [
    'validate_telegram_init_data',
    'extract_user_from_init_data'
]
