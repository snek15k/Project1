from django import forms
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings
from .models import User
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name, context, from_email=None, recipient_list=None, fail_silently=False, html_email_template_name=None,
                  extra_email_context=None):
        if extra_email_context:
            context.update(extra_email_context)

        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        html_message = loader.render_to_string(html_email_template_name, context) if html_email_template_name else None

        send_mail(subject, body, from_email, recipient_list, fail_silently=fail_silently, html_message=html_message)

    def save(self, domain_override=None,
             use_https=False,
             token_generator=None,
             from_email=None,
             request=None,
             email_template_name = None,
             subject_template_name = None,
             html_email_template_name=None,
             extra_email_context=None):

        return super().save(domain_override=domain_override,
                            use_https=use_https,
                            token_generator=token_generator,
                            from_email=from_email,
                            request=request,
                            email_template_name=email_template_name,
                            subject_template_name=subject_template_name,
                            html_email_template_name=html_email_template_name,
                            extra_email_context=extra_email_context)


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