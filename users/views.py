import secrets

from allauth.account.signals import password_reset
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

    def get_success_url(self):
        return reverse('users:password_reset_done')

    def form_valid(self, form):
        form.send_mail(
            self.request,
            form.cleaned_data['email'],
            subject_template_name=self.subject_template_name,
            email_template_name=self.email_template_name,
            from_email=settings.EMAIL_HOST_USER,
        )
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'users/registration/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')

    def dispatch(self, request, *args, **kwargs):
        self.verify_code = kwargs.get('verify_code')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['verify_code'] = self.verify_code
        return context

    def form_valid(self, form):
        user = get_object_or_404(User, verify_code=self.verify_code)
        form.save(user=user)
        return super().form_valid(form)


class RegisterView(CreateView):
    model = User
    template_name = 'registration/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        verify_code = user.generate_verify_code()
        user.is_active = False
        user.save()
        current_site = self.request.get_host()
        verification_url = reverse('users:email_confirm', kwargs={'token': verify_code})
        abs_verification_url = f"http://{current_site}{verification_url}"

        send_mail(
            subject='Подтверждение регистрации',
            message=f'Перейдите по ссылке для подтверждения почты: {abs_verification_url}',
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