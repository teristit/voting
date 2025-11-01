"""
Админ-панель для результатов
"""

from django.contrib import admin
from .models import SessionResult


@admin.register(SessionResult)
class SessionResultAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'session', 'rank', 'average_score', 'final_score',
        'bonus_amount', 'votes_received', 'calculated_at'
    )
    list_filter = ('session', 'rank', 'calculated_at')
    search_fields = ('user__first_name', 'user__last_name')
    raw_id_fields = ('session', 'user')
    
    readonly_fields = ('created_at', 'updated_at', 'calculated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('session', 'user')
        }),
        ('Алгоритм расчёта T1-T4', {
            'fields': (
                'raw_total_score', 'votes_received', 'average_score',
                'normalized_score', 'final_score'
            )
        }),
        ('Итоговые результаты', {
            'fields': ('rank', 'bonus_amount', 'bonus_percentage')
        }),
        ('Временные метки', {
            'fields': ('calculated_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session', 'user')