"""
API views для пользователей (минимальные, для бота)
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Получение профиля текущего пользователя
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserListView(generics.ListAPIView):
    """
    Список всех активных пользователей (для списка в голосовании)
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Только активные пользователи, которые могут получать голоса
        return User.objects.filter(
            is_active=True,
            can_receive_votes=True
        ).exclude(
            status='inactive'
        ).order_by('last_name', 'first_name')