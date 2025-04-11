import secrets
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, CreateView
from django.core.mail import send_mail
from config.settings import EMAIL_HOST_USER
from .forms import RegisterForm
from .models import User


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
        url = f"http://{host}/users/email-confirm/{token}/"
        send_mail(
            subject='Подтверждение регистрации',
            message=f'Перейдите по ссылке для подтверждения почты {url}',
            from_email=EMAIL_HOST_USER,
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
        return redirect(reverse('users:login'))


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'

    def get_queryset(self):
        if not self.request.user.is_staff:
            raise Http404()
        return User.objects.all()


class UserBlockView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, id=pk)
        if not request.user.is_staff:
            raise Http404('Вы не обладаете нужными правами')
        user.is_active = False
        user.save()
        return redirect(reverse('users:user_list'))


class UserUnblockView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(User, id=pk)
        if not request.user.is_staff:
            raise Http404('Вы не обладаете нужными правами')
        user.is_active = True
        user.save()
        return redirect(reverse('users:user_list'))
