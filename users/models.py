import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    "Модель пользователя"

    email = models.EmailField(unique=True, verbose_name="Email")
    avatar = models.ImageField(
        upload_to="avatars/", null=True, blank=True, verbose_name="Аватар"
    )
    phone = PhoneNumberField(blank=True, null=True, verbose_name=_("Номер телефона"))
    country = CountryField(blank=True, null=True, verbose_name=_("Страна"))
    is_active = models.BooleanField(default=True, null=True, blank=True)
    verification_token = models.CharField(max_length=100, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def generate_verification_token(self):
        "Генерация и сохранение токена верификации"
        self.verification_token = secrets.token_urlsafe(32)
        self.save()
        return self.verification_token

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ["email"]
        permissions = [
            ("block_user", _("Can block user")),
        ]
