from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from mail_messages.utils import is_manager
from .models import Mailing
from clients.models import Client
from attempt.models import MailingLog


def validate_mailing_time(mailing):
    "Проверка времени у рассылки"
    now = timezone.now()

    if mailing.status == "completed":
        raise ValidationError("Рассылка завершена и ее нельзя повторно запустить")

    if mailing.start_date_time and now < mailing.start_date_time:
        raise ValidationError("Рассылка еще не началась")

    if mailing.end_date_time and now > mailing.end_date_time:
        raise ValidationError("Рассылка уже завершена")

    if mailing.status != "started":
        mailing.status = "started"
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

        for client in mailing.clients.all():
            try:
                send_single_email(mailing, client)
            except Exception as e:
                MailingLog.objects.create(
                    mailing=mailing,
                    client=client,
                    status="not_successful",
                    server_response=str(e),
                )

        if mailing.end_date_time and timezone.now() > mailing.end_date_time:
            mailing.status = "completed"
            mailing.save()

    except Mailing.DoesNotExist:
        raise ValidationError(f"Рассылка с ID {mailing_id} не найдена.")
    except Exception as e:
        raise ValidationError(str(e))


def send_single_email(mailing, client):
    """Отправляет одно письмо конкретному клиенту."""
    if not client.email:
        raise ValueError("У клиента не указан email.")

    subject = mailing.message.message_subject
    message = mailing.message.message_body
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [client.email]

    send_mail(subject, message, from_email, recipient_list)
    MailingLog.objects.create(
        mailing=mailing, client=client, status="successfully", server_response="OK"
    )

def get_mailing_statistics(user=None):
    "Возвращает статистику рассылок для всех пользователей или для конкретного пользователя"

    if user and not is_manager(user):
        mailings = Mailing.objects.filter(owner=user)
    else:
        mailings = Mailing.objects.all()

    total_mailings = mailings.count()
    active_mailings_count = mailings.filter(is_active=True).count()
    unique_clients = Client.objects.filter(mailings__in=mailings).distinct().count()

    return {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings_count,
        "unique_clients": unique_clients,
    }