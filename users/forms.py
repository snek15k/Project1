from django import forms
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,
                                       SetPasswordForm, UserCreationForm)

from .models import User


class RegisterForm(UserCreationForm):
    "Форма регистрации с email"

    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2")


class LoginForm(AuthenticationForm):
    "Форма входа с email"

    username = forms.EmailField(label="Email")


class CustomPasswordResetForm(PasswordResetForm):
    "Форма сброса пароля"

    class Meta:
        model = User
        fields = ("email",)


class ChangePasswordForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields["new_password1"].widget.attrs.update({"class": "form-control"})
        self.fields["new_password2"].widget.attrs.update({"class": "form-control"})
