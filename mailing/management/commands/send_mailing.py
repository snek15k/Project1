from django.core.management.base import BaseCommand
from mailing.models import Mailing, MailingAttempt
from django.core.mail import send_mail
from django.utils import timezone

class Command(BaseCommand):
    help = 'Send mailing by ID'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID of the mailing to send')

    def handle(self, *args, **kwargs):
        mailing_id = kwargs['mailing_id']

        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            self.stderr.write(self.style.ERROR("Рассылка не найдена."))
            return

        if not mailing.is_active:
            self.stdout.write(self.style.WARNING("Рассылка отключена."))
            return

        mailing.status = 'Запущена'
        mailing.start_time = mailing.start_time or timezone.now()
        mailing.save()

        subject = mailing.message.subject
        body = mailing.message.body
        clients = mailing.clients.all()

        success = 0
        failed = 0

        for client in clients:
            try:
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=None,
                    recipient_list=[client.email],
                    fail_silently=False
                )
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='Успешно',
                    server_response='Отправлено успешно'
                )
                success += 1
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='Не успешно',
                    server_response=str(e)
                )
                failed += 1

        self.stdout.write(self.style.SUCCESS(f"Отправка завершена: успешно {success}, неудачно {failed}"))
