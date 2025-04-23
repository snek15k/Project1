import secrets

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='Аватар')
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='Номер телефона')
    country = models.CharField(max_length=50, null=True, blank=True, verbose_name='Страна')
    verify_code = models.CharField(max_length=64, verbose_name='Код верификации!', null=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name='Активный')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def generate_verify_code(self):
        self.verify_code = secrets.token_urlsafe(32)
        self.save()
        return self.verify_code


    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['email']
        permissions = [
            ("block_user", _("Can block user")),
        ]