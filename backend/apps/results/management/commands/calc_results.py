"""
Manage command: calc_results

Рассчитывает результаты T1–T4 для указанной сессии или всех завершённых.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP

from apps.sessions.models import VotingSession, BonusParameters, SessionParticipant
from apps.voting.models import Vote
from apps.results.models import SessionResult


class Command(BaseCommand):
    help = 'Рассчитать результаты (T1–T4) для сессий голосования'

    def add_arguments(self, parser):
        parser.add_argument('--session', type=int, help='ID сессии для перерасчёта')

    def handle(self, *args, **options):
        session_id = options.get('session')

        sessions = []
        if session_id:
            try:
                sessions = [VotingSession.objects.get(id=session_id)]
            except VotingSession.DoesNotExist:
                raise CommandError('Сессия не найдена')
        else:
            # По умолчанию считаем для завершённых сессий без calculated_at
            today = timezone.now().date()
            sessions = VotingSession.objects.filter(
                active=False,
                end_date__lt=today
            )

        for session in sessions:
            self.stdout.write(self.style.NOTICE(f'Processing session #{session.id}'))

            # Собираем голоса по получателям
            agg = Vote.objects.filter(session=session).values('target').annotate(
                total_score=Sum('score'),
                votes_count=Count('id'),
                avg_score=Avg('score'),
            )

            # Защита от деления на ноль
            totals = list(agg)
            if not totals:
                self.stdout.write(self.style.WARNING('Нет голосов в этой сессии'))
                continue

            # Нормализация T3: делим на максимум средней оценки
            max_avg = max(Decimal(str(a['avg_score'])) for a in totals)
            if max_avg <= 0:
                max_avg = Decimal('1.0')

            # Параметры премий (если есть)
            bonus_params = getattr(session, 'bonus_params', None)
            total_weekly_bonus = Decimal('0.00')
            if bonus_params:
                total_weekly_bonus = Decimal(bonus_params.total_weekly_bonus)

            # Создаём/обновляем результаты
            results = []
            for a in totals:
                user_id = a['target']
                t1 = Decimal(a['total_score'] or 0)
                votes_received = int(a['votes_count'] or 0)
                t2 = (Decimal(str(a['avg_score'])) if a['avg_score'] is not None else Decimal('0.00')).quantize(Decimal('0.01'))
                t3 = (t2 / max_avg).quantize(Decimal('0.001'))
                t4 = t3  # На данном этапе финальный = нормализованный

                result, _ = SessionResult.objects.update_or_create(
                    session=session,
                    user_id=user_id,
                    defaults={
                        'raw_total_score': t1,
                        'votes_received': votes_received,
                        'average_score': t2,
                        'normalized_score': t3,
                        'final_score': t4,
                    }
                )
                results.append(result)

            # Рейтинги
            results = sorted(results, key=lambda r: (r.final_score, r.average_score), reverse=True)
            for idx, r in enumerate(results, start=1):
                r.rank = idx
                r.save(update_fields=['rank'])

            # Распределение общей премии пропорционально final_score
            if total_weekly_bonus > 0:
                total_final = sum((r.final_score for r in results), Decimal('0.000'))
                if total_final <= 0:
                    per_user = (total_weekly_bonus / len(results)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    for r in results:
                        r.bonus_amount = per_user
                        r.bonus_percentage = (per_user / total_weekly_bonus * 100).quantize(Decimal('0.01'))
                        r.save(update_fields=['bonus_amount', 'bonus_percentage'])
                else:
                    for r in results:
                        share = (r.final_score / total_final)
                        amount = (share * total_weekly_bonus).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                        r.bonus_amount = amount
                        r.bonus_percentage = (share * 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                        r.save(update_fields=['bonus_amount', 'bonus_percentage'])

            self.stdout.write(self.style.SUCCESS(f'Session #{session.id} calculated: {len(results)} results'))
