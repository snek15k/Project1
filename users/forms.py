from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordResetForm,
    AuthenticationForm,
)
from .models import User


class RegisterForm(UserCreationForm):
    "Форма регистрации с email"
    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    "Форма входа с email"
    username = forms.EmailField(label='Email')


class CustomPasswordResetForm(PasswordResetForm):
    "Форма сброса пароля"
    class Meta:
        model = User
        fields = ('email',)



class ChangePasswordForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["password1", "password2"]