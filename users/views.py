from functools import reduce
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView, FormView, UpdateView,
    DetailView, TemplateView
)
from django.contrib.auth.views import (
    PasswordResetConfirmView,
    LogoutView,
)
from django.contrib import messages
from .forms import (
    RegisterForm, LoginForm,
    CustomPasswordResetForm, ChangePasswordForm
)
from .models import User
from django.conf import settings
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views


class RegisterView(CreateView):
    "Регистрация пользователя, отправка письма с токеном подверждения регистрации"
    form_class = RegisterForm
    template_name = 'users/registration/register.html'
    success_url = reverse_lazy('users:register')

    def form_valid(self, form):
        user = form.save(commit=False)
        token = user.generate_verification_token()
        user.is_active = False
        user.save()

        verification_link = f"{settings.DOMAIN}/users/verify/{token}/"
        send_mail(
            "Подтверждение регистрации в сервисе рассылок",
            f"Перейдите по ссылке для подтверждения: {verification_link}",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        messages.success(self.request, 'Письмо с подтверждением отправлено на вашу электронную почту')
        return super().form_valid(form)


class LoginView(FormView):
    "Аутентификация пользователя"
    form_class = LoginForm
    template_name = 'users/registration/login.html'
    success_url = reverse_lazy('clients:home')

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
           messages.error(self.request, 'Подтвердите ваш адрес электронной почты')
           return redirect('login')
        return super().form_valid(form)


class LogoutView(LogoutView):
    "Выход из системы"
    next_page = reverse_lazy('users:login')

#
# class ProfileView(LoginRequiredMixin, DetailView):
#     "Просмотр профиля пользователя"
#     model = User
#     template_name = 'users/registration/home.html'
#     context_object_name = 'profile_user'
#
#     def get_object(self):
#         return self.request.user
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['can_edit'] = True
#         return context


# class ProfileEditView(LoginRequiredMixin, UpdateView):
#     "Редактирование профиля пользователя"
#     form_class = ProfileEditForm
#     template_name = 'users/registration/profile_edit.html'
#     success_url = reverse_lazy('users:profile')
#
#     def get_object(self):
#         return self.request.user
#
#     def form_valid(self, form):
#         messages.success(self.request, 'Профиль успешно обновлен')
#         return super().form_valid(form)


class VerifyEmailView(TemplateView):
    """Подтверждение email по токену"""
    template_name = 'users/registration/verify_email.html'

    def get(self, request, token):
        try:
            user = User.objects.get(verification_token=token)
            user.is_active = True
            user.verification_token = ''
            user.save()
            messages.success(request, 'Ваша электронная почта успешно подтверждена.')
            return redirect('users:login')
        except User.DoesNotExist:
            messages.error(request, 'Недействительная ссылка подтверждения.')
            return redirect('users:register')


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'users/registration/password_reset.html'
    success_url = reverse_lazy('users:password_reset_done')
    form_class = CustomPasswordResetForm

    def form_valid(self, form):
        user = form.save(commit=False)
        token = user.generate_verification_token()

        verification_link = f"{settings.DOMAIN}/users/verify/{token}/"
        send_mail(
            "Восстановление пароля",
            f"Перейдите по ссылке для смены пароля: {verification_link}",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        messages.success(self.request, 'Письмо со ссылкой для смены пароля отправлено на вашу электронную почту')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    "Установка нового пароля, сброс старого"
    form_class = ChangePasswordForm
    template_name = 'users/registration/password_reset_confirm.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Пароль успешно изменён')
        return response