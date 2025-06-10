from django.db import models
from django.utils import timezone

from clients.models import Client
from mailings.models import Mailing


class MailingLog(models.Model):
    "Модель попытка рассылки"

    STATUS_CHOICES = [
        ("successfully", "Успешно"),
        ("not_successful", "Не успешно"),
    ]

    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        verbose_name="Рассылка",
        related_name="attempts",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name="Получатель",
        related_name="attempts",
    )
    date_time = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата и время попытки",
        db_index=True,
        editable=False,
    )
    status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default="not_successful",
        verbose_name="Статус",
        db_index=True,
    )
    server_response = models.TextField(
        verbose_name="Ответ почтового сервера", blank=True, null=True
    )

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
        ordering = ["-date_time"]

    def __str__(self):
        return (
            f"{self.mailing} - {self.client.email} - {self.date_time} - {self.status}"
        )

    @classmethod
    def get_user_stats(cls, user):
        """Общая статистика по пользователю"""
        logs = cls.objects.filter(mailing__owner=user)
        total = logs.count()
        success = logs.filter(status="successfully").count()
        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "success_rate": (success / total * 100) if total > 0 else 0,
        }
