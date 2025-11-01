# Smart Award Django Project
# Система "Умная премия" для еженедельного голосования сотрудников

__version__ = '1.0.0-dev'
__author__ = 'teristit'
__description__ = 'Информационная система для еженедельного взаимного голосования сотрудников с автоматическим расчетом премий'

# Celery app import
from .celery import app as celery_app

__all__ = ('celery_app',)