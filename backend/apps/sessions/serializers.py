"""
DRF сериализаторы для сессий
"""

from rest_framework import serializers
from .models import VotingSession, SessionParticipant, BonusParameters


class VotingSessionSerializer(serializers.ModelSerializer):
    """
    Сериализатор сессии голосования
    """
    participants_count = serializers.IntegerField(source='get_participants_count', read_only=True)
    voters_count = serializers.IntegerField(source='get_voters_count', read_only=True)
    participation_rate = serializers.FloatField(source='get_participation_rate', read_only=True)
    is_current = serializers.BooleanField(read_only=True)
    can_vote_today = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = VotingSession
        fields = [
            'id', 'start_date', 'end_date', 'active', 'auto_participants',
            'participants_count', 'voters_count', 'participation_rate',
            'is_current', 'can_vote_today', 'created_at', 'closed_at'
        ]
        read_only_fields = ['id', 'created_at', 'closed_at']


class SessionParticipantSerializer(serializers.ModelSerializer):
    """
    Сериализатор участника сессии
    """
    user_name = serializers.CharField(source='user.get_display_name', read_only=True)
    
    class Meta:
        model = SessionParticipant
        fields = [
            'id', 'user', 'user_name', 'can_vote', 'can_receive_votes', 'participant_status'
        ]