"""
DRF сериализаторы для голосования
"""

from rest_framework import serializers
from .models import Vote


class VoteSerializer(serializers.ModelSerializer):
    """
    Сериализатор голоса
    """
    voter_name = serializers.CharField(source='voter.get_display_name', read_only=True)
    target_name = serializers.CharField(source='target.get_display_name', read_only=True)
    
    class Meta:
        model = Vote
        fields = [
            'id', 'session', 'voter', 'target', 'voter_name', 'target_name',
            'score', 'modified_by_admin', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class VoteCastSerializer(serializers.Serializer):
    """
    Сериализатор для отправки голосов
    """
    session_id = serializers.IntegerField()
    votes = serializers.ListField(
        child=serializers.DictField()
    )