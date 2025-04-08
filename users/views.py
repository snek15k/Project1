from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import RegisterForm
from django.core.mail import send_mail
from django.conf import settings
from .models import User
from django.contrib import messages

class RegisterView(CreateView):
    model = User
    template_name = 'registration/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        user = form.save()
        self.send_welcome_email(user.email)
        messages.success(self.request, 'Вы успешно зарегистрированы.  Проверьте свою почту.')
        return super().form_valid(form)

    def send_welcome_email(self, email):
        subject = 'Добро пожаловать!'
        message = 'Спасибо за регистрацию на нашем сайте.'
        from_email = settings.EMAIL_HOST_USER
        try:
            send_mail(subject, message, from_email, [email])
        except Exception as e:
            self.handle_email_error(e)
            messages.error(self.request, 'Произошла ошибка при отправке приветственного письма.  Попробуйте позже.')


    def handle_email_error(self, error):
        print(f"Ошибка при отправке email: {error}")

