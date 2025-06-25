from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

class Client(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='clients')
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f'{self.full_name} <{self.email}>'


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.subject


class MailingStatus(models.TextChoices):
    CREATED = 'Создана'
    RUNNING = 'Запущена'
    FINISHED = 'Завершена'


class Mailing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='mailings')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=MailingStatus.choices,
        default=MailingStatus.CREATED
    )
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Mailing #{self.id} - {self.status}"


class MailingAttemptStatus(models.TextChoices):
    SUCCESS = 'Успешно'
    FAILURE = 'Не успешно'


class MailingAttempt(models.Model):
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=MailingAttemptStatus.choices)
    server_response = models.TextField()

    def __str__(self):
        return f"Attempt for mailing {self.mailing.id} at {self.timestamp} - {self.status}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return f'Profile: {self.user.username}'

# Автоматическое создание профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
