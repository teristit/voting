"""
Celery configuration for smart_award project.

This module configures Celery for background task processing including:
- Automatic session creation
- Results calculation
- Export generation
- Notifications
- Backup tasks
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_award.settings')

app = Celery('smart_award')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
app.conf.beat_schedule = {
    'create-weekly-sessions': {
        'task': 'apps.sessions.tasks.create_weekly_session',
        'schedule': 60.0 * 60.0 * 24.0,  # Every day
        'options': {'expires': 60.0 * 60.0 * 2.0}  # Task expires in 2 hours
    },
    'calculate-session-results': {
        'task': 'apps.results.tasks.calculate_expired_sessions',
        'schedule': 60.0 * 60.0,  # Every hour
    },
    'send-reminder-notifications': {
        'task': 'apps.telegram_bot.tasks.send_voting_reminders',
        'schedule': 60.0 * 60.0 * 12.0,  # Twice a day
    },
    'cleanup-expired-tokens': {
        'task': 'apps.authentication.tasks.cleanup_expired_tokens',
        'schedule': 60.0 * 60.0 * 24.0,  # Daily
    },
    'backup-database': {
        'task': 'apps.core.tasks.create_database_backup',
        'schedule': 60.0 * 60.0 * 24.0,  # Daily at 2 AM
        'options': {
            'expires': 60.0 * 60.0 * 4.0,  # Task expires in 4 hours
        }
    },
}

app.conf.timezone = settings.TIME_ZONE

# Task routing
app.conf.task_routes = {
    'apps.telegram_bot.tasks.*': {'queue': 'telegram'},
    'apps.results.tasks.*': {'queue': 'calculations'},
    'apps.analytics.tasks.*': {'queue': 'reports'},
    'apps.core.tasks.*': {'queue': 'system'},
}

# Task configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone=settings.TIME_ZONE,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')