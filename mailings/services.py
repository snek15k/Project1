from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Mailing
from attempt.models import MailingLog


def validate_mailing_time(mailing):
    "Проверка времени у рассылки"
    now = timezone.now()

    if mailing.status == 'completed':
        raise ValidationError("Рассылка завершена и ее нельзя повторно запустить")

    if mailing.start_date_time and now < mailing.start_date_time:
        mailing.status = 'created'
        mailing.save()
        raise ValidationError("Рассылка еще не началась")

    if mailing.end_date_time and now > mailing.end_date_time:
        mailing.status = 'completed'
        mailing.save()
        raise ValidationError("Рассылка уже завершена")

    if mailing.status != 'started':
        mailing.status = 'started'
        if not mailing.start_date_time:
            mailing.start_date_time = now
        mailing.save()


def send_mailing(mailing_id):
    """Отправка рассылки"""
    try:
        mailing = Mailing.objects.get(pk=mailing_id)

        validate_mailing_time(mailing)

        if not mailing.clients.exists():
            raise ValidationError("Нет получателей для рассылки.")

        successful_sends = 0
        for client in mailing.clients.all():
            try:
                send_single_email(mailing, client)
                successful_sends += 1
            except Exception as e:
                print(f"Ошибка при отправке рассылки {mailing.id} получателю {client.email}: {e}")

        if mailing.end_date_time and timezone.now() > mailing.end_date_time:
            mailing.status = 'completed'
            mailing.save()

        return successful_sends

    except Mailing.DoesNotExist:
        raise ValidationError(f"Рассылка с ID {mailing_id} не найдена.")
    except Exception as e:
        raise ValidationError(str(e))


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
