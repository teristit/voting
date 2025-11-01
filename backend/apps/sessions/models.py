"""
Модели для сессий голосования
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
import json

User = get_user_model()


class VotingSession(models.Model):
    """
    Сессия голосования (обычно еженедельная)
    """
    
    start_date = models.DateField(
        help_text="Дата начала сессии"
    )
    end_date = models.DateField(
        help_text="Дата окончания сессии"
    )
    
    active = models.BooleanField(
        default=True,
        help_text="Активна ли сессия"
    )
    auto_participants = models.BooleanField(
        default=True,
        help_text="Автоматически добавлять всех активных пользователей"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Время закрытия сессии"
    )
    
    class Meta:
        db_table = 'voting_sessions'
        verbose_name = 'Сессия голосования'
        verbose_name_plural = 'Сессии голосования'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"Сессия #{self.id} ({self.start_date} - {self.end_date})"
    
    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError('Дата окончания не может быть раньше даты начала')
    
    def is_current(self):
        """Проверяет, является ли сессия текущей"""
        today = timezone.now().date()
        return (
            self.active and 
            self.start_date <= today <= self.end_date
        )
    
    def can_vote_today(self):
        """Можно ли сегодня голосовать"""
        return self.is_current() and not self.closed_at
    
    def get_participants_count(self):
        """Количество участников"""
        return self.participants.count()
    
    def get_voters_count(self):
        """Количество проголосовавших"""
        from apps.voting.models import Vote
        return Vote.objects.filter(session=self).values('voter').distinct().count()
    
    def get_participation_rate(self):
        """Процент участия"""
        participants = self.get_participants_count()
        voters = self.get_voters_count()
        if participants == 0:
            return 0.0
        return (voters / participants) * 100


class SessionParticipant(models.Model):
    """
    Участник сессии голосования
    """
    
    PARTICIPANT_STATUS_CHOICES = [
        ('active', 'Участвует'),
        ('excluded', 'Исключён'),
        ('on_leave', 'В отпуске'),
        ('sick_leave', 'На больничном'),
    ]
    
    session = models.ForeignKey(
        VotingSession, 
        on_delete=models.CASCADE, 
        related_name='participants'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='session_participations'
    )
    
    can_vote = models.BooleanField(
        default=True,
        help_text="Может ли голосовать в этой сессии"
    )
    can_receive_votes = models.BooleanField(
        default=True,
        help_text="Может ли получать голоса в этой сессии"
    )
    participant_status = models.CharField(
        max_length=20, 
        choices=PARTICIPANT_STATUS_CHOICES, 
        default='active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'session_participants'
        verbose_name = 'Участник сессии'
        verbose_name_plural = 'Участники сессий'
        unique_together = ['session', 'user']
    
    def __str__(self):
        return f"{self.user.get_display_name()} в {self.session}"


class BonusParameters(models.Model):
    """
    Параметры расчёта премий для сессии
    """
    
    session = models.OneToOneField(
        VotingSession, 
        on_delete=models.CASCADE, 
        related_name='bonus_params'
    )
    
    # Параметры для расчёта премий
    average_weekly_revenue = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Средний недельный доход"
    )
    participation_multiplier = models.DecimalField(
        max_digits=4, 
        decimal_places=3,
        default=1.000,
        help_text="Множитель участия"
    )
    total_weekly_bonus = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Общий размер недельной премии"
    )
    
    # Информация об участниках (JSON в TextField для SQLite)
    participants_info_json = models.TextField(
        blank=True,
        default='{}',
        help_text="JSON с информацией об участниках"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bonus_parameters'
        verbose_name = 'Параметры премий'
        verbose_name_plural = 'Параметры премий'
    
    def __str__(self):
        return f"Параметры {self.session}"
    
    @property
    def participants_info(self):
        """Парсит информацию об участниках"""
        try:
            return json.loads(self.participants_info_json or '{}')
        except json.JSONDecodeError:
            return {}
    
    @participants_info.setter
    def participants_info(self, value):
        """Сохраняет информацию об участниках"""
        self.participants_info_json = json.dumps(value or {})