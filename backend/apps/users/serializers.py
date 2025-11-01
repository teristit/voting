"""
DRF сериализаторы для пользователей
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор пользователя
    """
    display_name = serializers.CharField(source='get_display_name', read_only=True)
    full_name = serializers.CharField(source='get_display_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'display_name', 'full_name',
            'first_name', 'last_name', 'middle_name',
            'telegram_id', 'telegram_username',
            'position', 'department', 'role', 'status',
            'can_vote', 'can_receive_votes',
            'is_active', 'last_login', 'last_vote_date'
        ]
        read_only_fields = ['id', 'last_login', 'last_vote_date']


class UserVotingSerializer(serializers.ModelSerializer):
    """
    Упрощённый сериализатор для списка в голосовании
    """
    display_name = serializers.CharField(source='get_display_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'display_name', 'position', 'department']
        read_only_fields = ['id', 'display_name', 'position', 'department']