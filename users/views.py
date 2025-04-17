import secrets

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, LoginView
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, CreateView
from django.core.mail import send_mail
from config.settings import EMAIL_HOST_USER
from .forms import RegisterForm, CustomSetPasswordForm, CustomPasswordResetForm
from .models import User
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'users/registration/password_reset.html'
    email_template_name = 'users/registration/password_reset_email.html'
    subject_template_name = 'users/registration/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')

    def form_valid(self, form):
        form.save(
            use_https=self.request.is_secure(),
            token_generator=self.token_generator,
            from_email=settings.EMAIL_HOST_USER,
            request=self.request,
        )
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'users/registration/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class RegisterView(CreateView):
    model = User
    template_name = 'registration/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        token = secrets.token_hex(32)
        user.token = token
        user.is_active = False
        user.save()
        host = self.request.get_host()
        url = f"https://{host}/users/email-confirm/{token}/"
        send_mail(
            subject='Подтверждение регистрации',
            message=f'Перейдите по ссылке для подтверждения почты {url}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return super().form_valid(form)


class EmailConfirmView(View):
    def get(self, request, token):
        user = get_object_or_404(User, token=token)
        user.is_active = True
        user.token = ''
        user.save()
        messages.success(request, 'Ваша учетная запись успешно активирована! Пожалуйста, войдите.')
        return redirect(reverse('users:login'))


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'

    def get_queryset(self):
        if not self.request.user.is_staff:
            raise Http404()
        return User.objects.all()


class UserBlockView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('users:block_user',)

    def get(self, request, pk):
        user = get_object_or_404(User, id=pk)
        if not request.user.is_staff:
            raise Http404('Вы не обладаете нужными правами')
        user.is_active = False
        user.save()
        return redirect(reverse('users:user_list'))


class UserUnblockView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('users:unblock_user',)

    def get(self, request, pk):
        user = get_object_or_404(User, id=pk)
        if not request.user.is_staff:
            raise Http404('Вы не обладаете нужными правами')
        user.is_active = True
        user.save()
        return redirect(reverse('users:user_list'))


@login_required
def profile_view(request):
    return render(request, 'users/profile.html')


class LoginView(LoginView):
    template_name = 'registration/login.html'


class LogoutView(View):
    next_page = reverse_lazy('clients:home')