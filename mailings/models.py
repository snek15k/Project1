from allauth.account.views import email
from django.db import models

from clients.models import Client
from mail_messages.models import Message


class Mailing(models.Model):
    "Модель управления рассылками"
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name='Дата и время начала рассылки', auto_now_add=True, db_index=True)
    end_time = models.DateTimeField(verbose_name='Дата и время окончания рассылки', db_index=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='created', verbose_name='Статус', db_index=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='Сообщение')
    recipients = models.ManyToManyField(Client, verbose_name='Получатели')

    def __str__(self):
        return f'Рассылка: {self.message} | Статус: {self.get_status_display()}'


    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

