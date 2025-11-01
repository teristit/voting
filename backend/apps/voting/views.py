"""
API views для голосования
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from apps.sessions.models import VotingSession
from .models import Vote
from .serializers import VoteSerializer, VoteCastSerializer
import logging

logger = logging.getLogger('smart_award')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cast_votes(request):
    """
    Отправка голосов от пользователя
    
    Ожидаемый формат:
    {
        "session_id": 1,
        "votes": [
            {"target_id": 2, "score": 8},
            {"target_id": 3, "score": 6}
        ]
    }
    """
    try:
        session_id = request.data.get('session_id')
        votes_data = request.data.get('votes', [])
        
        if not session_id:
            return Response(
                {'error': 'Не указан session_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем сессию
        try:
            session = VotingSession.objects.get(id=session_id)
        except VotingSession.DoesNotExist:
            return Response(
                {'error': 'Сессия не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not session.can_vote_today():
            return Response(
                {'error': 'Сессия завершена или неактивна'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем, может ли пользователь голосовать
        participant = session.participants.filter(
            user=request.user,
            can_vote=True,
            participant_status='active'
        ).first()
        
        if not participant:
            return Response(
                {'error': 'Вы не можете участвовать в этой сессии'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Обрабатываем голоса в транзакции
        with transaction.atomic():
            created_votes = []
            updated_votes = []
            
            for vote_data in votes_data:
                target_id = vote_data.get('target_id')
                score = vote_data.get('score')
                
                if target_id == request.user.id:
                    continue  # Пропускаем голос за себя
                
                try:
                    target_user = User.objects.get(id=target_id)
                except User.DoesNotExist:
                    continue
                
                # Проверяем, может ли target получать голоса
                target_participant = session.participants.filter(
                    user=target_user,
                    can_receive_votes=True
                ).first()
                
                if not target_participant:
                    continue
                
                # Создаём или обновляем голос
                vote, created = Vote.objects.update_or_create(
                    session=session,
                    voter=request.user,
                    target=target_user,
                    defaults={'score': score}
                )
                
                if created:
                    created_votes.append(vote)
                else:
                    updated_votes.append(vote)
        
        logger.info(f"User {request.user.id} cast votes in session {session_id}: "
                   f"{len(created_votes)} new, {len(updated_votes)} updated")
        
        return Response({
            'success': True,
            'message': f'Голоса сохранены',
            'votes_created': len(created_votes),
            'votes_updated': len(updated_votes)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error casting votes: {e}", exc_info=True)
        return Response(
            {'error': 'Ошибка при сохранении голосов'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_votes(request):
    """
    Получение голосов текущего пользователя в активной сессии
    """
    today = timezone.now().date()
    session = VotingSession.objects.filter(
        active=True,
        start_date__lte=today,
        end_date__gte=today
    ).first()
    
    if not session:
        return Response({'votes': []})
    
    votes = Vote.objects.filter(
        session=session,
        voter=request.user
    ).select_related('target')
    
    serializer = VoteSerializer(votes, many=True)
    return Response({
        'session_id': session.id,
        'votes': serializer.data
    })