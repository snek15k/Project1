from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
    AuthenticationForm,
    UserChangeForm,
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


class ProfileEditForm(UserChangeForm):
    "Форма редактирования профиля"
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone', 'country', 'avatar')


class CustomPasswordResetForm(PasswordResetForm):
    "Форма сброса пароля"
    email = forms.EmailField(
                             max_length=254,
                             label='Email',
                             widget=forms.EmailInput(attrs={'autocomplete': 'Email'}),
                             )


class CustomSetPasswordForm(SetPasswordForm):
    "Форма для нового пароля (если пользователь забыл старый)"
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'autocomplete': 'Password'}),
        strip=False,
        )

    new_password2 = forms.CharField(
        label='Подтвердите новый пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'Password'}),
    )