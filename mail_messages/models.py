from django.db import models


class Message(models.Model):
    "Модель управления сообщениями"
    message_subject = models.CharField(max_length=100, verbose_name='Тема письма', null=False, blank=False)
    message_body = models.TextField(verbose_name='Текст письма', null=False, blank=False)


    def __str__(self):
        return self.message_subject


    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
