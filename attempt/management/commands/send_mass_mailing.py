from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from attempt.models import MailingLog
from clients.models import Client
from mailings.models import Mailing


class Command(BaseCommand):
    help = 'Отправляет массовую рассылку по ID рассылки'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки, которую нужно отправить')

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            raise CommandError(f'Рассылка с ID "{mailing_id}" не найдена.')

        if not mailing.is_active:
            self.stdout.write(self.style.WARNING(f'Рассылка с ID "{mailing_id}" не активна. Отправка не будет произведена.'))
            return

        clients = Client.objects.all()

        for client in clients:
            try:
                send_mail(
                    mailing.title,
                    mailing.body,
                    settings.EMAIL_HOST_USER,
                    [client.email],
                    fail_silently=False,
                )
                MailingLog.objects.create(
                    mailing=mailing,
                    client=client,
                    status='successfully',
                    date_time=timezone.now(),
                )
                self.stdout.write(self.style.SUCCESS(f'Успешно отправлено клиенту: {client.email}'))

            except Exception as e:
                MailingLog.objects.create(
                    mailing=mailing,
                    client=client,
                    status='not_successful',
                    server_response=str(e),
                    date_time=timezone.now(),
                )
                self.stdout.write(self.style.ERROR(f'Ошибка отправки клиенту {client.email}: {e}'))

        self.stdout.write(self.style.SUCCESS('Рассылка успешно завершена.'))