"""
Админ-панель для сессий голосования
"""

from django.contrib import admin
from .models import VotingSession, SessionParticipant, BonusParameters


class SessionParticipantInline(admin.TabularInline):
    model = SessionParticipant
    extra = 0
    fields = ('user', 'can_vote', 'can_receive_votes', 'participant_status')
    raw_id_fields = ('user',)


class BonusParametersInline(admin.StackedInline):
    model = BonusParameters
    max_num = 1
    fields = ('average_weekly_revenue', 'participation_multiplier', 'total_weekly_bonus')


@admin.register(VotingSession)
class VotingSessionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'start_date', 'end_date', 'active', 'auto_participants',
        'get_participants_count', 'get_voters_count', 'get_participation_rate'
    )
    list_filter = ('active', 'auto_participants', 'start_date')
    date_hierarchy = 'start_date'
    
    inlines = [BonusParametersInline, SessionParticipantInline]
    
    fieldsets = (
        (None, {
            'fields': ('start_date', 'end_date', 'active', 'auto_participants')
        }),
        ('Техническая информация', {
            'fields': ('created_at', 'closed_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'closed_at')
    
    def get_participants_count(self, obj):
        return obj.get_participants_count()
    get_participants_count.short_description = 'Участников'
    
    def get_voters_count(self, obj):
        return obj.get_voters_count()
    get_voters_count.short_description = 'Проголосовало'
    
    def get_participation_rate(self, obj):
        return f"{obj.get_participation_rate():.1f}%"
    get_participation_rate.short_description = 'Участие'


@admin.register(SessionParticipant)
class SessionParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'session', 'can_vote', 'can_receive_votes', 'participant_status'
    )
    list_filter = ('can_vote', 'can_receive_votes', 'participant_status', 'session')
    raw_id_fields = ('session', 'user')
    search_fields = ('user__first_name', 'user__last_name', 'user__username')


@admin.register(BonusParameters)
class BonusParametersAdmin(admin.ModelAdmin):
    list_display = (
        'session', 'average_weekly_revenue', 'participation_multiplier', 'total_weekly_bonus'
    )
    raw_id_fields = ('session',)