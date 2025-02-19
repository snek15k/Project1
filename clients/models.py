from django.db import models


class Client(models.Model):
    "Модель получатель рассылки"
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=100, verbose_name='Ф.И.О')
    comment = models.TextField(verbose_name='Комментарий')


    def __str__(self):
        return self.email


    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'



