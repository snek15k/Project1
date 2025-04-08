import smtplib
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from requests.exceptions import RequestException
from django.db import IntegrityError, DatabaseError
from .models import Mailing, MailingAttempt
from clients.models import Client

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
    mailing.end_date_time = timezone.now()
    mailing.save()

    for client in mailing.clients.all():
        try:
            send_single_email(mailing, client)
        except Exception as e:
            print(f"Ошибка при отправке рассылки {mailing.id} получателю {client.email}: {e}")


def send_single_email(mailing, client):
    """Отправляет одно письмо конкретному клиенту и обрабатывает ошибки."""
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

    except ValueError as e:
        status = 'not_successful'
        if "У клиента не указан email" in str(e):
            server_response = "У клиента не указан email."
        else:
            server_response = f"Некорректный email: {e}"
        raise

    except RequestException as e:
        status = 'not_successful'
        server_response = f"Ошибка сети: Не удалось подключиться к сети или серверу. Проверьте подключение к интернету."

    except smtplib.SMTPException as e:
        status = 'not_successful'
        server_response = f"Ошибка SMTP: {e}"

    except smtplib.SMTPRecipientsRefused as e:
        status = 'not_successful'
        server_response = f"Ошибка SMTP: Сервер отклонил одного или нескольких получателей.  Возможно, email адрес не существует или заблокирован."

    except smtplib.SMTPAuthenticationError as e:
        status = 'not_successful'
        server_response = f"Ошибка SMTP: Не удалось пройти аутентификацию на почтовом сервере. Проверьте логин и пароль в настройках."

    except (IntegrityError, DatabaseError) as e:
        status = 'not_successful'
        server_response = f"Ошибка базы данных: Произошла ошибка при записи данных в базу данных.  Обратитесь к администратору."

    except Exception as e:
        # Любые другие ошибки
        status = 'not_successful'
        server_response = f"Неизвестная ошибка: {type(e).__name__} - {e}"

    finally:
        # Создаем запись о попытке рассылки в любом случае
        MailingAttempt.objects.create(mailing=mailing, client=client, status=status, server_response=server_response)