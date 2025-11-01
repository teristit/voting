"""
Сервис экспорта данных
Обеспечивает экспорт результатов в форматы XLSX и CSV
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from io import BytesIO
from flask import current_app
from sqlalchemy import text
from extensions import db
from models.session import Session, SessionParticipant
from models.vote import Vote
from models.result import Result
from models.user import User
from models.bonus import BonusParameters
import logging

logger = logging.getLogger(__name__)


class ExportService:
    """Сервис экспорта данных"""
    
    @staticmethod
    def export_session_results(session_id: int, format_type: str = 'xlsx') -> Tuple[bytes, str]:
        """
        Экспорт результатов сессии
        
        Args:
            session_id: ID сессии
            format_type: Формат экспорта ('xlsx' или 'csv')
        
        Returns:
            Tuple[байты файла, имя файла]
        """
        try:
            # Получаем данные сессии
            session = Session.query.get(session_id)
            if not session:
                raise ValueError(f"Сессия {session_id} не найдена")
            
            # Получаем результаты
            results = db.session.query(
                Result,
                User.name,
                User.telegram_username
            ).join(
                User, Result.user_id == User.user_id
            ).filter(
                Result.session_id == session_id
            ).order_by(Result.rank).all()
            
            if not results:
                raise ValueError(f"Результаты для сессии {session_id} не найдены")
            
            # Получаем параметры бонусов
            bonus_params = BonusParameters.query.filter_by(session_id=session_id).first()
            
            # Формируем данные для экспорта
            export_data = []
            for result, name, telegram_username in results:
                calc_details = result.calculation_details or {}
                
                export_data.append({
                    'Ранг': result.rank,
                    'Имя': name,
                    'Telegram': telegram_username or '',
                    'Средняя оценка': float(result.average_score),
                    'Количество голосов': result.votes_received,
                    'Бонус (руб.)': float(result.total_bonus),
                    'T1 (сырые оценки)': str(calc_details.get('T1_raw_scores', [])),
                    'T2 (средняя)': calc_details.get('T2_average', 0),
                    'T3 (нормализованная)': calc_details.get('T3_normalized', 0),
                    'T4 (финальная)': calc_details.get('T4_final', 0)
                })
            
            # Создаем DataFrame
            df = pd.DataFrame(export_data)
            
            # Генерируем имя файла
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"session_{session_id}_results_{timestamp}.{format_type}"
            
            if format_type.lower() == 'xlsx':
                return ExportService._create_excel_file(df, session, bonus_params), filename
            else:
                return ExportService._create_csv_file(df), filename
                
        except Exception as e:
            logger.error(f"Ошибка при экспорте результатов сессии {session_id}: {str(e)}")
            raise
    
    @staticmethod
    def _create_excel_file(df: pd.DataFrame, session: Session, 
                          bonus_params: Optional[BonusParameters]) -> bytes:
        """
        Создаем Excel файл с данными
        """
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Основные результаты
            df.to_excel(writer, sheet_name='Результаты', index=False)
            
            # Информация о сессии
            session_info = pd.DataFrame([
                ['Период сессии', f"{session.start_date} - {session.end_date}"],
                ['Статус', 'Активна' if session.active else 'Закрыта'],
                ['Дата создания', session.created_at.strftime('%Y-%m-%d %H:%M:%S') if session.created_at else ''],
                ['Дата закрытия', session.closed_at.strftime('%Y-%m-%d %H:%M:%S') if session.closed_at else 'Не закрыта']
            ], columns=['Параметр', 'Значение'])
            
            session_info.to_excel(writer, sheet_name='Инфо о сессии', index=False)
            
            # Параметры бонусов
            if bonus_params:
                bonus_info = pd.DataFrame([
                    ['Средненедельная выручка', float(bonus_params.average_weekly_revenue or 0)],
                    ['Множитель участия', float(bonus_params.participation_multiplier or 0)],
                    ['Общий недельный бонус', float(bonus_params.total_weekly_bonus or 0)]
                ], columns=['Параметр', 'Значение'])
                
                bonus_info.to_excel(writer, sheet_name='Параметры бонусов', index=False)
        
        output.seek(0)
        return output.read()
    
    @staticmethod
    def _create_csv_file(df: pd.DataFrame) -> bytes:
        """
        Создаем CSV файл
        """
        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')  # utf-8-sig для Excel
        output.seek(0)
        return output.read()
    
    @staticmethod
    def export_participants_data(session_id: int, format_type: str = 'xlsx') -> Tuple[bytes, str]:
        """
        Экспорт данных об участниках
        """
        try:
            # Получаем данные об участниках
            participants = db.session.query(
                SessionParticipant,
                User.name,
                User.telegram_username,
                User.telegram_id
            ).join(
                User, SessionParticipant.user_id == User.user_id
            ).filter(
                SessionParticipant.session_id == session_id
            ).all()
            
            if not participants:
                raise ValueError(f"Участники сессии {session_id} не найдены")
            
            # Получаем статистику по голосам
            votes_stats = db.session.query(
                Vote.voter_id,
                db.func.count(Vote.vote_id).label('votes_given')
            ).filter(
                Vote.session_id == session_id
            ).group_by(Vote.voter_id).all()
            
            votes_given_dict = {stat.voter_id: stat.votes_given for stat in votes_stats}
            
            # Формируем данные
            export_data = []
            for participant, name, telegram_username, telegram_id in participants:
                export_data.append({
                    'Имя': name,
                    'Telegram логин': telegram_username or '',
                    'Telegram ID': telegram_id or '',
                    'Может голосовать': 'Да' if participant.can_vote else 'Нет',
                    'Может получать голоса': 'Да' if participant.can_receive_votes else 'Нет',
                    'Статус': participant.status,
                    'Проголосовал': votes_given_dict.get(participant.user_id, 0),
                    'Дата добавления': participant.created_at.strftime('%Y-%m-%d %H:%M:%S') if participant.created_at else ''
                })
            
            df = pd.DataFrame(export_data)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"session_{session_id}_participants_{timestamp}.{format_type}"
            
            if format_type.lower() == 'xlsx':
                output = BytesIO()
                df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)
                return output.read(), filename
            else:
                return ExportService._create_csv_file(df), filename
                
        except Exception as e:
            logger.error(f"Ошибка при экспорте участников сессии {session_id}: {str(e)}")
            raise
    
    @staticmethod
    def export_payment_data(session_id: int, format_type: str = 'csv') -> Tuple[bytes, str]:
        """
        Экспорт данных для выплат (бухгалтерия)
        """
        try:
            # Получаем результаты с бонусами > 0
            payment_data = db.session.query(
                Result,
                User.name,
                User.telegram_username,
                User.telegram_id
            ).join(
                User, Result.user_id == User.user_id
            ).filter(
                Result.session_id == session_id,
                Result.total_bonus > 0
            ).order_by(Result.rank).all()
            
            if not payment_data:
                raise ValueError(f"Данные для выплат по сессии {session_id} не найдены")
            
            # Формируем данные для бухгалтерии
            export_data = []
            for result, name, telegram_username, telegram_id in payment_data:
                export_data.append({
                    'ФИО': name,
                    'Telegram': telegram_username or '',
                    'Telegram ID': telegram_id or '',
                    'Сумма к выплате (руб.)': float(result.total_bonus),
                    'Оценка': float(result.average_score),
                    'Место': result.rank,
                    'Комментарий': f'Бонус за сессию {session_id}'
                })
            
            df = pd.DataFrame(export_data)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"session_{session_id}_payments_{timestamp}.{format_type}"
            
            if format_type.lower() == 'xlsx':
                output = BytesIO()
                df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)
                return output.read(), filename
            else:
                return ExportService._create_csv_file(df), filename
                
        except Exception as e:
            logger.error(f"Ошибка при экспорте данных для выплат {session_id}: {str(e)}")
            raise
    
    @staticmethod
    def export_full_analytics(session_ids: List[int], format_type: str = 'xlsx') -> Tuple[bytes, str]:
        """
        Полный экспорт аналитики по нескольким сессиям
        """
        try:
            all_results = []
            
            for session_id in session_ids:
                # Получаем результаты каждой сессии
                session_results = db.session.query(
                    Result,
                    User.name,
                    Session.start_date,
                    Session.end_date
                ).join(
                    User, Result.user_id == User.user_id
                ).join(
                    Session, Result.session_id == Session.session_id
                ).filter(
                    Result.session_id == session_id
                ).order_by(Result.rank).all()
                
                for result, name, start_date, end_date in session_results:
                    all_results.append({
                        'Сессия ID': session_id,
                        'Период': f"{start_date} - {end_date}",
                        'Имя': name,
                        'Место': result.rank,
                        'Оценка': float(result.average_score),
                        'Бонус': float(result.total_bonus),
                        'Голосов получено': result.votes_received
                    })
            
            if not all_results:
                raise ValueError("Нет данных для экспорта")
            
            df = pd.DataFrame(all_results)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"full_analytics_{timestamp}.{format_type}"
            
            if format_type.lower() == 'xlsx':
                output = BytesIO()
                df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)
                return output.read(), filename
            else:
                return ExportService._create_csv_file(df), filename
                
        except Exception as e:
            logger.error(f"Ошибка при полном аналитическом экспорте: {str(e)}")
            raise
