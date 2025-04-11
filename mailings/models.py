from allauth.account.views import email
from django.db import models
from django.conf import settings

from clients.models import Client
from mail_messages.models import Message


class Mailing(models.Model):
    "Модель управления рассылками"
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    name = models.CharField(max_length=150, verbose_name='Название рассылки')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='Сообщение', related_name='mailings')
    clients = models.ManyToManyField(Client, verbose_name='Клиенты', related_name='mailings')
    start_date_time = models.DateTimeField(verbose_name='Дата и время первой отправки', blank=True, null=True,
                                           editable=False)
    end_date_time = models.DateTimeField(verbose_name='Дата и время окончания отправки', blank=True, null=True,
                                         editable=False)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='created', verbose_name='Статус',
                              db_index=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец', )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    is_active = models.BooleanField(default=True, verbose_name='Активна')


    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        permissions = [
            ("can_view_mailing", "Can view mailing")
        ]


    def get_successful_attempts_count(self):
        return self.attempt.filter(status='successfully').count()

    def get_unsuccessful_attempts_count(self):
        return self.attempts.filter(status='not_unsuccessful').count()

    def total_attempts_count(self):
        return self.attempts.count()

    def __str__(self):
        return f'Рассылка: {self.message} | Статус: {self.get_status_display()}'

