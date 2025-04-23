import secrets

import form
from django import forms
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.template import loader
from django.conf import settings
from .models import User
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        user.verify_code = user.generate_verify_code()
        if commit:
            user.save()
        return user


class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, request, recipient_email, subject_template_name, email_template_name, from_email=None, html_email_template_name=None):

        user = get_object_or_404(User, email=recipient_email)
        verify_code = user.generate_verify_code()
        user.save()

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        context = {
            'email': recipient_email,
            'domain': request.get_host(),
            'site_name': 'Your Site',
            'uidb64': uidb64,
            'token': token,
            'verify_code': verify_code,
            'protocol': 'http',
        }

        subject = render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        text_content = render_to_string(email_template_name, context)

        if html_email_template_name:
            html_content = render_to_string(html_email_template_name, context)
        else:
            html_content = None

        send_mail(subject, text_content, from_email or settings.DEFAULT_FROM_EMAIL, [recipient_email], html_message=html_content)


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите новый пароль'}),
        strip=False,
        help_text='Пароль должен содержать не менее 8 символов'
    )
    new_password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтвердите новый пароль'}),
        strip = False,
    )

    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password1")
        confirm_password = cleaned_data.get("new_password2")

        if password != confirm_password:
            raise forms.ValidationError(
                "Пароли не совпадают"
            )
    def save(self, commit=True, user=None):
        if user:
            user.set_password(self.cleaned_data["new_password1"])
            if commit:
                user.save()
        return user