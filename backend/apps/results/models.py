"""
Модели результатов голосования
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SessionResult(models.Model):
    """
    Результаты пользователя в сессии голосования
    """
    
    session = models.ForeignKey(
        'sessions.VotingSession',
        on_delete=models.CASCADE,
        related_name='results'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='session_results'
    )
    
    # Алгоритм T1-T4 (по документации)
    raw_total_score = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0.00,
        help_text="T1: Сумма сырых баллов"
    )
    votes_received = models.PositiveIntegerField(
        default=0,
        help_text="Количество полученных голосов"
    )
    average_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        help_text="T2: Средняя оценка"
    )
    normalized_score = models.DecimalField(
        max_digits=6, 
        decimal_places=3, 
        default=0.000,
        help_text="T3: Нормализованный балл"
    )
    final_score = models.DecimalField(
        max_digits=6, 
        decimal_places=3, 
        default=0.000,
        help_text="T4: Финальный балл (с корректировками)"
    )
    
    # Рейтинг и премия
    rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Место в рейтинге"
    )
    bonus_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Размер премии"
    )
    bonus_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        help_text="Процент от общей премии"
    )
    
    # Временные метки
    calculated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Когда были посчитаны результаты"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'session_results'
        verbose_name = 'Результат сессии'
        verbose_name_plural = 'Результаты сессий'
        unique_together = ['session', 'user']
        ordering = ['-final_score']
    
    def __str__(self):
        return f"{self.user.get_display_name()} в {self.session}: {self.final_score}"