"""
Модели пользователей для системы Smart Award (адаптировано под SQLite)
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import json


class User(AbstractUser):
    """
    Основная модель пользователя системы Smart Award
    Наследует AbstractUser и добавляет Telegram интеграцию
    """
    
    ROLE_CHOICES = [
        ('user', 'Сотрудник'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('inactive', 'Неактивный'),
        ('on_leave', 'В отпуске'),
        ('sick_leave', 'На больничном'),
    ]
    
    # Telegram интеграция
    telegram_id = models.BigIntegerField(
        unique=True, 
        null=True, 
        blank=True,
        help_text="ID пользователя в Telegram"
    )
    telegram_username = models.CharField(
        max_length=100, 
        blank=True, 
        default='',
        help_text="Username в Telegram"
    )
    
    # Профиль
    middle_name = models.CharField(
        max_length=150, 
        blank=True, 
        default='',
        help_text="Отчество"
    )
    position = models.CharField(
        max_length=200, 
        blank=True, 
        default='',
        help_text="Должность"
    )
    department = models.CharField(
        max_length=200, 
        blank=True, 
        default='',
        help_text="Отдел"
    )
    
    # Роль и статус
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='user'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active'
    )
    
    # Права в системе голосования
    can_vote = models.BooleanField(
        default=True,
        help_text="Может голосовать"
    )
    can_receive_votes = models.BooleanField(
        default=True,
        help_text="Может получать голоса"
    )
    
    # Метаданные (для SQLite используем TextField вместо JSONField)
    permissions_json = models.TextField(
        blank=True, 
        default='{}',
        help_text="JSON с дополнительными разрешениями"
    )
    
    # Временные метки
    last_vote_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Последнее голосование"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return self.get_display_name()
    
    def get_display_name(self):
        """Полное имя для отображения"""
        parts = [self.last_name, self.first_name, self.middle_name]
        full_name = ' '.join(filter(None, parts))
        return full_name or self.username or f"Пользователь #{self.id}"
    
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    def is_manager(self):
        return self.role in ['manager', 'admin'] or self.is_superuser
    
    def is_voting_eligible(self):
        """Может ли участвовать в голосовании"""
        return (
            self.is_active and 
            self.status == 'active' and 
            self.can_vote
        )
    
    def can_be_voted_for(self):
        """Может ли быть объектом голосования"""
        return (
            self.is_active and 
            self.status in ['active', 'on_leave'] and 
            self.can_receive_votes
        )
    
    @property
    def permissions(self):
        """Парсит дополнительные разрешения из JSON"""
        try:
            return json.loads(self.permissions_json or '{}')
        except json.JSONDecodeError:
            return {}
    
    @permissions.setter
    def permissions(self, value):
        """Сохраняет дополнительные разрешения в JSON"""
        self.permissions_json = json.dumps(value or {})