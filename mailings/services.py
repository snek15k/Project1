from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import Mailing
from attempt.models import MailingLog


def send_mailing(mailing_id):
    """Отправляет рассылку по ее ID."""
    try:
        mailing = Mailing.objects.get(pk=mailing_id)
    except Mailing.DoesNotExist:
        raise ValueError(f"Рассылка с ID {mailing_id} не найдена.")

    if mailing.status == 'completed':
        raise ValueError("Рассылка уже завершена и её нельзя повторно запустить.")

    if mailing.start_date_time is None:
        mailing.start_date_time = timezone.now()
        mailing.status = 'Запущена'
    mailing.save()

    for client in mailing.clients.all():
        try:
            send_single_email(mailing, client)
        except Exception as e:
            print(f"Ошибка при отправке рассылки {mailing.id} получателю {client.email}: {e}")


def send_single_email(mailing, client):
    """Отправляет одно письмо конкретному клиенту и обрабатывает ошибки."""
    status = 'not_successful'
    server_response = None

    try:
        if not client.email:
            raise ValueError("У клиента не указан email.")

        subject = mailing.message.message_subject
        message = mailing.message.message_body
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [client.email]

        send_mail(subject, message, from_email, recipient_list)
        status = 'successfully'
        server_response = 'OK'

    except Exception as e:
        server_response = str(e)

    finally:
        MailingLog.objects.create(mailing=mailing, client=client, status=status, server_response=server_response)
