"""
Модель голосования
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings

User = get_user_model()


class Vote(models.Model):
    """
    Голос в сессии голосования
    """
    
    session = models.ForeignKey(
        'sessions.VotingSession',
        on_delete=models.CASCADE,
        related_name='votes'
    )
    voter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votes_given',
        help_text="Кто голосует"
    )
    target = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votes_received',
        help_text="За кого голосуют"
    )
    
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10)
        ],
        help_text="Оценка 0-10"
    )
    
    # Технические поля
    modified_by_admin = models.BooleanField(
        default=False,
        help_text="Изменён админом"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'votes'
        verbose_name = 'Голос'
        verbose_name_plural = 'Голоса'
        unique_together = ['session', 'voter', 'target']  # Один голос от каждого за каждого
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.voter.get_display_name()} → {self.target.get_display_name()}: {self.score}"
    
    def clean(self):
        # Проверка: нельзя голосовать за себя
        if self.voter == self.target:
            raise ValidationError('Нельзя голосовать за себя')
        
        # Проверка диапазона оценки
        min_score = settings.SMART_AWARD['VOTE_SCALE_MIN']
        max_score = settings.SMART_AWARD['VOTE_SCALE_MAX']
        if not (min_score <= self.score <= max_score):
            raise ValidationError(f'Оценка должна быть от {min_score} до {max_score}')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        # Обновляем дату последнего голосования
        self.voter.last_vote_date = self.created_at
        self.voter.save(update_fields=['last_vote_date'])