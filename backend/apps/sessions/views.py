"""
API views для сессий голосования (минимальные)
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import VotingSession, SessionParticipant
from .serializers import VotingSessionSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_session(request):
    """
    Получение текущей активной сессии
    """
    today = timezone.now().date()
    session = VotingSession.objects.filter(
        active=True,
        start_date__lte=today,
        end_date__gte=today
    ).first()
    
    if not session:
        return Response({
            'message': 'Нет активных сессий',
            'session': None
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = VotingSessionSerializer(session)
    return Response({
        'session': serializer.data,
        'can_user_vote': session.participants.filter(
            user=request.user, 
            can_vote=True, 
            participant_status='active'
        ).exists()
    })


class SessionListView(generics.ListAPIView):
    """
    Список всех сессий (для админа)
    """
    serializer_class = VotingSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return VotingSession.objects.all().order_by('-start_date')