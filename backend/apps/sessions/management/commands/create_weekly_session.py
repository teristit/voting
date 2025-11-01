from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.sessions.models import VotingSession, SessionParticipant
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Создать новую недельную сессию и автоматически добавить участников'

    def handle(self, *args, **options):
        today = timezone.now().date()
        start = today - timezone.timedelta(days=today.weekday())
        end = start + timezone.timedelta(days=6)

        session, created = VotingSession.objects.get_or_create(
            start_date=start,
            end_date=end,
            defaults={'active': True, 'auto_participants': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Создана сессия #{session.id} ({start} - {end})'))
        else:
            self.stdout.write(self.style.WARNING(f'Сессия уже существует #{session.id} ({start} - {end})'))

        if session.auto_participants:
            users = User.objects.filter(is_active=True, can_vote=True)
            added = 0
            for u in users:
                obj, created = SessionParticipant.objects.get_or_create(
                    session=session,
                    user=u,
                    defaults={'can_vote': True, 'can_receive_votes': True, 'participant_status': 'active'}
                )
                if created:
                    added += 1
            self.stdout.write(self.style.SUCCESS(f'Добавлено участников: {added}'))
