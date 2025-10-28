"""
Сервис для расчета результатов голосования
Реализация алгоритма T1-T4 согласно документации
"""

from typing import Dict, List, Tuple, Optional
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy import text
from extensions import db
from models.vote import Vote
from models.session import Session, SessionParticipant
from models.bonus import BonusParameters
from models.result import Result
from models.user import User
import logging

logger = logging.getLogger(__name__)


class CalculationService:
    """Сервис для расчета результатов голосования"""
    
    @staticmethod
    def calculate_session_results(session_id: int) -> Dict:
        """
        Основная функция расчета результатов сессии
        
        Args:
            session_id: ID сессии голосования
            
        Returns:
            Dict с результатами расчета
        """
        try:
            # Получаем данные сессии
            session = Session.query.get(session_id)
            if not session:
                raise ValueError(f"Сессия {session_id} не найдена")
            
            # Получаем параметры бонусов
            bonus_params = BonusParameters.query.filter_by(session_id=session_id).first()
            if not bonus_params:
                raise ValueError(f"Параметры бонусов для сессии {session_id} не найдены")
            
            # Получаем участников, которые могут получать голоса
            participants = db.session.query(
                SessionParticipant.user_id,
                User.name
            ).join(
                User, SessionParticipant.user_id == User.user_id
            ).filter(
                SessionParticipant.session_id == session_id,
                SessionParticipant.can_receive_votes == True,
                SessionParticipant.status == 'active'
            ).all()
            
            if not participants:
                raise ValueError(f"Нет активных участников для сессии {session_id}")
            
            # Получаем все голоса
            votes = Vote.query.filter_by(session_id=session_id).all()
            
            # Выполняем расчеты T1-T4
            t1_data = CalculationService._calculate_t1(votes, participants)
            t2_data = CalculationService._calculate_t2(t1_data)
            t3_data = CalculationService._calculate_t3(t2_data)
            t4_data = CalculationService._calculate_t4(t3_data, bonus_params)
            
            # Сохраняем результаты
            CalculationService._save_results(session_id, t4_data, t1_data, t2_data, t3_data)
            
            return {
                'session_id': session_id,
                'status': 'success',
                'participants_count': len(participants),
                'votes_count': len(votes),
                'results': t4_data,
                'calculation_details': {
                    'T1': t1_data,
                    'T2': t2_data,
                    'T3': t3_data,
                    'T4': t4_data
                }
            }
            
        except Exception as e:
            logger.error(f"Ошибка при расчете результатов сессии {session_id}: {str(e)}")
            raise
    
    @staticmethod
    def _calculate_t1(votes: List[Vote], participants: List[Tuple]) -> Dict:
        """
        T1: Матрица сырых оценок
        """
        # Создаем словарь для хранения оценок
        raw_scores = {}
        
        for participant in participants:
            user_id = participant[0]
            # Получаем все оценки для этого участника
            user_votes = [v.score for v in votes if v.target_id == user_id]
            raw_scores[user_id] = user_votes
        
        return raw_scores
    
    @staticmethod
    def _calculate_t2(t1_data: Dict) -> Dict:
        """
        T2: Средние оценки
        """
        average_scores = {}
        
        for user_id, scores in t1_data.items():
            if scores:  # Проверяем, что есть оценки
                avg_score = sum(scores) / len(scores)
                # Округляем до 2 знаков после запятой
                average_scores[user_id] = float(Decimal(str(avg_score)).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                ))
            else:
                average_scores[user_id] = 0.0
        
        return average_scores
    
    @staticmethod
    def _calculate_t3(t2_data: Dict) -> Dict:
        """
        T3: Нормализованные оценки (масштабирование 0-10)
        """
        if not t2_data:
            return {}
        
        scores = list(t2_data.values())
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 10
        
        normalized_scores = {}
        
        # Если все оценки одинаковые, возвращаем их как есть
        if max_score == min_score:
            return t2_data.copy()
        
        for user_id, score in t2_data.items():
            # Нормализация в диапазон 0-10
            normalized_score = ((score - min_score) / (max_score - min_score)) * 10
            normalized_scores[user_id] = float(Decimal(str(normalized_score)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            ))
        
        return normalized_scores
    
    @staticmethod
    def _calculate_t4(t3_data: Dict, bonus_params: BonusParameters) -> Dict:
        """
        T4: Итоговые оценки с распределением бонусов
        """
        if not t3_data:
            return {}
        
        total_weekly_bonus = float(bonus_params.total_weekly_bonus or 0)
        participation_multiplier = float(bonus_params.participation_multiplier or 1.0)
        
        # Применяем множитель участия
        adjusted_scores = {}
        for user_id, score in t3_data.items():
            adjusted_scores[user_id] = score * participation_multiplier
        
        # Вычисляем общую сумму оценок
        total_score = sum(adjusted_scores.values())
        
        final_results = {}
        
        if total_score > 0:
            # Распределяем бонусы пропорционально оценкам
            for user_id, score in adjusted_scores.items():
                bonus_amount = (score / total_score) * total_weekly_bonus
                final_results[user_id] = {
                    'final_score': float(Decimal(str(score)).quantize(
                        Decimal('0.01'), rounding=ROUND_HALF_UP
                    )),
                    'bonus_amount': float(Decimal(str(bonus_amount)).quantize(
                        Decimal('0.01'), rounding=ROUND_HALF_UP
                    ))
                }
        else:
            # Если общая сумма 0, распределяем поровну
            participants_count = len(adjusted_scores)
            if participants_count > 0:
                equal_bonus = total_weekly_bonus / participants_count
                for user_id in adjusted_scores.keys():
                    final_results[user_id] = {
                        'final_score': 0.0,
                        'bonus_amount': float(Decimal(str(equal_bonus)).quantize(
                            Decimal('0.01'), rounding=ROUND_HALF_UP
                        ))
                    }
        
        return final_results
    
    @staticmethod
    def _save_results(session_id: int, t4_data: Dict, t1_data: Dict, 
                     t2_data: Dict, t3_data: Dict) -> None:
        """
        Сохраняем результаты в базу данных
        """
        try:
            # Удаляем старые результаты
            Result.query.filter_by(session_id=session_id).delete()
            
            # Создаем ранжированный список по финальным оценкам
            sorted_results = sorted(
                t4_data.items(),
                key=lambda x: x[1]['final_score'],
                reverse=True
            )
            
            # Сохраняем результаты
            for rank, (user_id, data) in enumerate(sorted_results, 1):
                votes_received = len(t1_data.get(user_id, []))
                
                result = Result(
                    session_id=session_id,
                    user_id=user_id,
                    average_score=Decimal(str(data['final_score'])),
                    rank=rank,
                    total_bonus=Decimal(str(data['bonus_amount'])),
                    votes_received=votes_received,
                    calculation_details={
                        'T1_raw_scores': t1_data.get(user_id, []),
                        'T2_average': t2_data.get(user_id, 0.0),
                        'T3_normalized': t3_data.get(user_id, 0.0),
                        'T4_final': data['final_score']
                    }
                )
                
                db.session.add(result)
            
            db.session.commit()
            logger.info(f"Результаты для сессии {session_id} успешно сохранены")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при сохранении результатов: {str(e)}")
            raise

    @staticmethod
    def get_session_statistics(session_id: int) -> Dict:
        """
        Получаем статистику по сессии
        """
        try:
            # Общая статистика по участникам
            participants_stats = db.session.query(
                db.func.count(SessionParticipant.participant_id).label('total_participants'),
                db.func.count(db.case([(SessionParticipant.can_vote == True, 1)])).label('can_vote'),
                db.func.count(db.case([(SessionParticipant.can_receive_votes == True, 1)])).label('can_receive'),
                db.func.count(db.case([(SessionParticipant.status == 'active', 1)])).label('active')
            ).filter(SessionParticipant.session_id == session_id).first()
            
            # Статистика по голосам
            votes_stats = db.session.query(
                db.func.count(Vote.vote_id).label('total_votes'),
                db.func.count(db.func.distinct(Vote.voter_id)).label('voted_users'),
                db.func.avg(Vote.score).label('average_score')
            ).filter(Vote.session_id == session_id).first()
            
            return {
                'session_id': session_id,
                'participants': {
                    'total': participants_stats.total_participants or 0,
                    'can_vote': participants_stats.can_vote or 0,
                    'can_receive_votes': participants_stats.can_receive or 0,
                    'active': participants_stats.active or 0
                },
                'votes': {
                    'total_votes': votes_stats.total_votes or 0,
                    'voted_users': votes_stats.voted_users or 0,
                    'average_score': float(votes_stats.average_score or 0),
                    'participation_rate': (
                        (votes_stats.voted_users or 0) / max(participants_stats.can_vote or 1, 1) * 100
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики сессии {session_id}: {str(e)}")
            raise
