from django.db import models
from django.utils import timezone
from mailings.models import Mailing


class MailingAttempt(models.Model):
    "Модель попытка рассылки"
    STATUS_CHOICES = [
        ('successfully', 'Успешно'),
        ('not_successful', 'Не успешно'),
    ]

    date_time = models.DateTimeField(default=timezone.now, verbose_name='Дата и время попытки', db_index=True, editable=False)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='not_successful',verbose_name='Статус', db_index=True)
    server_response = models.TextField(verbose_name='Ответ почтового сервера')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name='Рассылка', related_name='attempts')

    def __str__(self):
        return f'Попытка рассылки: {self.date_time} - {self.get_status_display()}'


