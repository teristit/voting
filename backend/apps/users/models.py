"""
Модели пользователей для системы «Умная премия»

Этот модуль содержит Django модели для управления пользователями системы голосования.
Интегрируется с Django Auth и предоставляет дополнительную функциональность.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.postgres.fields import JSONField
import uuid


class User(AbstractUser):
    """
    Расширенная модель пользователя для системы голосования
    
    Наследует от AbstractUser Django и добавляет специфичные для системы поля
    """
    
    # Роли пользователей
    ROLE_CHOICES = [
        ('user', 'Сотрудник'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
        ('super_admin', 'Супер-администратор'),
    ]
    
    # Статусы пользователя
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('inactive', 'Неактивный'),
        ('on_leave', 'В отпуске'),
        ('sick_leave', 'На больничном'),
        ('suspended', 'Приостановлен'),
    ]
    
    # Дополнительные поля профиля
    telegram_id = models.BigIntegerField(
        unique=True, 
        null=True, 
        blank=True,
        help_text="ID пользователя в Telegram"
    )
    telegram_username = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        help_text="Username в Telegram (без @)"
    )
    
    # Персональная информация
    middle_name = models.CharField(
        max_length=150, 
        blank=True,
        help_text="Отчество"
    )
    position = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Должность"
    )
    department = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Отдел"
    )
    employee_id = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Табельный номер сотрудника"
    )
    
    # Контактные данные
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Номер телефона должен быть в формате: '+999999999'. До 15 цифр."
    )
    phone = models.CharField(
        validators=[phone_validator], 
        max_length=17, 
        blank=True,
        help_text="Номер телефона"
    )
    
    # Рабочая информация
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='user',
        help_text="Роль пользователя в системе"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        help_text="Текущий статус пользователя"
    )
    
    hire_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Дата приема на работу"
    )
    termination_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Дата увольнения"
    )
    
    # Настройки системы голосования
    can_vote = models.BooleanField(
        default=True,
        help_text="Может ли пользователь голосовать"
    )
    can_receive_votes = models.BooleanField(
        default=True,
        help_text="Может ли пользователь получать голоса"
    )
    voting_weight = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=1.00,
        help_text="Весовой коэффициент голосов пользователя (обычно 1.0)"
    )
    
    # Метаданные и настройки
    permissions = JSONField(
        default=dict, 
        blank=True,
        help_text="Дополнительные разрешения пользователя"
    )
    preferences = JSONField(
        default=dict, 
        blank=True,
        help_text="Персональные настройки пользователя"
    )
    metadata = JSONField(
        default=dict, 
        blank=True,
        help_text="Дополнительные метаданные"
    )
    
    # Временные метки
    last_vote_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Дата последнего голосования"
    )
    last_login_telegram = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Последний вход через Telegram"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Дата создания записи"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Дата последнего обновления"
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['telegram_id']),
            models.Index(fields=['role']),
            models.Index(fields=['status']),
            models.Index(fields=['department']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        parts = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(filter(None, parts))
    
    def get_display_name(self):
        """Возвращает имя для отображения"""
        full_name = self.get_full_name()
        if full_name:
            return full_name
        return self.username or f"Пользователь #{self.id}"
    
    def is_admin(self):
        """Проверяет, является ли пользователь администратором"""
        return self.role in ['admin', 'super_admin']
    
    def is_manager(self):
        """Проверяет, является ли пользователь менеджером"""
        return self.role in ['manager', 'admin', 'super_admin']
    
    def is_voting_eligible(self):
        """Проверяет, может ли пользователь участвовать в голосовании"""
        return (
            self.is_active and 
            self.status == 'active' and 
            self.can_vote
        )
    
    def is_vote_target_eligible(self):
        """Проверяет, может ли пользователь быть объектом голосования"""
        return (
            self.is_active and 
            self.status in ['active', 'on_leave'] and 
            self.can_receive_votes
        )
    
    def has_telegram_access(self):
        """Проверяет, настроен ли доступ через Telegram"""
        return bool(self.telegram_id)
    
    def get_role_display_icon(self):
        """Возвращает иконку для роли пользователя"""
        icons = {
            'user': '👤',
            'manager': '👔',
            'admin': '👨‍💼',
            'super_admin': '🔑',
        }
        return icons.get(self.role, '👤')
    
    def get_status_display_icon(self):
        """Возвращает иконку для статуса пользователя"""
        icons = {
            'active': '✅',
            'inactive': '❌',
            'on_leave': '🏖️',
            'sick_leave': '🏥',
            'suspended': '⏸️',
        }
        return icons.get(self.status, '❓')
    
    def update_last_login_telegram(self):
        """Обновляет время последнего входа через Telegram"""
        self.last_login_telegram = timezone.now()
        self.save(update_fields=['last_login_telegram'])
    
    def update_last_vote_date(self):
        """Обновляет дату последнего голосования"""
        self.last_vote_date = timezone.now()
        self.save(update_fields=['last_vote_date'])
    
    def get_permissions_list(self):
        """Возвращает список дополнительных разрешений"""
        return self.permissions.get('additional_permissions', [])
    
    def add_permission(self, permission: str):
        """Добавляет дополнительное разрешение"""
        permissions = self.get_permissions_list()
        if permission not in permissions:
            permissions.append(permission)
            self.permissions['additional_permissions'] = permissions
            self.save(update_fields=['permissions'])
    
    def remove_permission(self, permission: str):
        """Удаляет дополнительное разрешение"""
        permissions = self.get_permissions_list()
        if permission in permissions:
            permissions.remove(permission)
            self.permissions['additional_permissions'] = permissions
            self.save(update_fields=['permissions'])


class UserProfile(models.Model):
    """
    Расширенный профиль пользователя с дополнительной информацией
    """
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    # Персональные данные
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True,
        help_text="Аватар пользователя"
    )
    birth_date = models.DateField(
        null=True, 
        blank=True,
        help_text="Дата рождения"
    )
    bio = models.TextField(
        max_length=500, 
        blank=True,
        help_text="Краткая биография"
    )
    
    # Рабочая информация
    skills = JSONField(
        default=list, 
        blank=True,
        help_text="Навыки и компетенции"
    )
    achievements = JSONField(
        default=list, 
        blank=True,
        help_text="Достижения и награды"
    )
    projects = JSONField(
        default=list, 
        blank=True,
        help_text="Участие в проектах"
    )
    
    # Статистика голосований
    total_votes_given = models.PositiveIntegerField(
        default=0,
        help_text="Общее количество отданных голосов"
    )
    total_votes_received = models.PositiveIntegerField(
        default=0,
        help_text="Общее количество полученных голосов"
    )
    average_rating = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=0.00,
        help_text="Средний рейтинг за все время"
    )
    best_rating = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=0.00,
        help_text="Лучший рейтинг за сессию"
    )
    
    # Настройки уведомлений
    notifications_enabled = models.BooleanField(
        default=True,
        help_text="Включены ли уведомления"
    )
    email_notifications = models.BooleanField(
        default=True,
        help_text="Email уведомления"
    )
    telegram_notifications = models.BooleanField(
        default=True,
        help_text="Telegram уведомления"
    )
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f"Профиль {self.user.get_display_name()}"
    
    def get_skills_list(self):
        """Возвращает список навыков"""
        return self.skills if isinstance(self.skills, list) else []
    
    def add_skill(self, skill: str):
        """Добавляет навык"""
        skills = self.get_skills_list()
        if skill not in skills:
            skills.append(skill)
            self.skills = skills
            self.save(update_fields=['skills'])
    
    def remove_skill(self, skill: str):
        """Удаляет навык"""
        skills = self.get_skills_list()
        if skill in skills:
            skills.remove(skill)
            self.skills = skills
            self.save(update_fields=['skills'])
    
    def calculate_rating_stats(self):
        """Пересчитывает статистику рейтингов"""
        from apps.results.models import SessionResult
        
        results = SessionResult.objects.filter(user=self.user)
        
        if results.exists():
            self.average_rating = results.aggregate(
                avg_rating=models.Avg('average_score')
            )['avg_rating'] or 0.00
            
            self.best_rating = results.aggregate(
                max_rating=models.Max('average_score')
            )['max_rating'] or 0.00
            
            self.save(update_fields=['average_rating', 'best_rating'])


class UserActivity(models.Model):
    """
    Модель для отслеживания активности пользователей
    """
    
    ACTION_CHOICES = [
        ('login', 'Вход в систему'),
        ('vote_cast', 'Отдача голоса'),
        ('session_view', 'Просмотр сессии'),
        ('results_view', 'Просмотр результатов'),
        ('profile_update', 'Обновление профиля'),
        ('telegram_interaction', 'Взаимодействие с ботом'),
        ('admin_action', 'Административное действие'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='activities'
    )
    action = models.CharField(
        max_length=50, 
        choices=ACTION_CHOICES
    )
    description = models.TextField(
        blank=True,
        help_text="Подробное описание действия"
    )
    metadata = JSONField(
        default=dict, 
        blank=True,
        help_text="Дополнительные данные о действии"
    )
    
    # Техническая информация
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="IP адрес пользователя"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User Agent браузера"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activities'
        verbose_name = 'Активность пользователя'
        verbose_name_plural = 'Активности пользователей'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_display_name()} - {self.get_action_display()}"


# Сигналы для автоматического создания профилей
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Создает профиль пользователя при создании пользователя"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Сохраняет профиль пользователя при сохранении пользователя"""
    if hasattr(instance, 'profile'):
        instance.profile.save()