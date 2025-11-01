"""
API views для результатов
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import SessionResult
from .serializers import SessionResultSerializer
from apps.sessions.models import VotingSession


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_results(request):
    """
    Получение результатов текущего пользователя
    """
    session_id = request.GET.get('session_id')
    
    if session_id:
        # Конкретная сессия
        try:
            session = VotingSession.objects.get(id=session_id)
            result = SessionResult.objects.get(session=session, user=request.user)
            serializer = SessionResultSerializer(result)
            return Response(serializer.data)
        except (VotingSession.DoesNotExist, SessionResult.DoesNotExist):
            return Response(
                {'error': 'Результаты не найдены'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        # Последние результаты
        results = SessionResult.objects.filter(
            user=request.user
        ).select_related('session').order_by('-session__end_date')[:5]
        
        serializer = SessionResultSerializer(results, many=True)
        return Response({
            'results': serializer.data
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_results(request, session_id):
    """
    Получение всех результатов сессии (только для админов)
    """
    if not request.user.is_admin():
        return Response(
            {'error': 'Недостаточно прав'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        session = VotingSession.objects.get(id=session_id)
        results = SessionResult.objects.filter(
            session=session
        ).select_related('user').order_by('rank')
        
        serializer = SessionResultSerializer(results, many=True)
        return Response({
            'session_id': session_id,
            'results': serializer.data
        })
        
    except VotingSession.DoesNotExist:
        return Response(
            {'error': 'Сессия не найдена'},
            status=status.HTTP_404_NOT_FOUND
        )