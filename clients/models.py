from django.db import models
from django.conf import settings

class Client(models.Model):
    "Модель получатель рассылки"
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=100, verbose_name='ФИО', null=False, blank=False)
    comment = models.TextField(verbose_name='Комментарий', null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец', )


    def __str__(self):
        return self.email


    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ('email',)



