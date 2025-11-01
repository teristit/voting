"""
DRF сериализаторы для результатов
"""

from rest_framework import serializers
from .models import SessionResult


class SessionResultSerializer(serializers.ModelSerializer):
    """
    Сериализатор результата сессии
    """
    user_name = serializers.CharField(source='user.get_display_name', read_only=True)
    session_period = serializers.SerializerMethodField()
    
    class Meta:
        model = SessionResult
        fields = [
            'id', 'session', 'user', 'user_name', 'session_period',
            'raw_total_score', 'votes_received', 'average_score',
            'normalized_score', 'final_score', 'rank',
            'bonus_amount', 'bonus_percentage',
            'calculated_at', 'created_at'
        ]
    
    def get_session_period(self, obj):
        return {
            'start_date': obj.session.start_date,
            'end_date': obj.session.end_date
        }