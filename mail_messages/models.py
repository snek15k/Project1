from django.db import models
from django.conf import settings


class Message(models.Model):
    "Модель управления сообщениями"
    message_subject = models.CharField(max_length=100, verbose_name='Тема письма', null=False, blank=False)
    message_body = models.TextField(verbose_name='Текст письма', null=False, blank=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец')

    def __str__(self):
        return self.message_subject


    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['message_subject']
        permissions = [
            ('can_view_message', 'Can view message'),
        ]