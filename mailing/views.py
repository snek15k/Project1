from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
)
from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


class HomePageView(TemplateView):
    template_name = 'mailing/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='Запущена').count()
        context['unique_clients'] = Client.objects.count()
        return context


# ===== Client Views =====
@method_decorator(cache_page(60 * 5), name='dispatch')
class ClientListView(ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Менеджеры').exists():
            return super().get_queryset()
        return super().get_queryset().filter(owner=user)


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('client-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('client-list')

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(owner=user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user and not request.user.is_superuser:
            messages.error(request, "Нет прав для редактирования этого клиента.")
            return redirect('client-list')
        return super().dispatch(request, *args, **kwargs)


class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'mailing/client_confirm_delete.html'
    success_url = reverse_lazy('client-list')

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(owner=user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user and not request.user.is_superuser:
            messages.error(request, "Нет прав для удаления этого клиента.")
            return redirect('client-list')
        return super().dispatch(request, *args, **kwargs)


# ===== Message Views (общие) =====
class MessageListView(ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('message-list')


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('message-list')


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('message-list')


# ===== Mailing Views =====
class MailingListView(ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Менеджеры').exists():
            return super().get_queryset()
        return super().get_queryset().filter(owner=user)


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing-list')

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(owner=user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user and not request.user.is_superuser:
            messages.error(request, "Нет прав для редактирования этой рассылки.")
            return redirect('mailing-list')
        return super().dispatch(request, *args, **kwargs)


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing-list')

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(owner=user)

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user and not request.user.is_superuser:
            messages.error(request, "Нет прав для удаления этой рассылки.")
            return redirect('mailing-list')
        return super().dispatch(request, *args, **kwargs)


# ===== Отправка рассылки вручную =====
class MailingSendView(View):

    def post(self, request, pk):
        mailing = Mailing.objects.get(pk=pk)

        if not mailing.is_active:
            messages.warning(request, "Рассылка отключена.")
            return redirect('mailing-list')

        if mailing.owner != request.user and not request.user.is_superuser:
            messages.error(request, "Нет прав на отправку этой рассылки.")
            return redirect('mailing-list')

        mailing.status = 'Запущена'
        mailing.start_time = mailing.start_time or timezone.now()
        mailing.save()

        clients = mailing.clients.all()
        subject = mailing.message.subject
        body = mailing.message.body

        success_count = 0
        failure_count = 0

        for client in clients:
            try:
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='Успешно',
                    server_response='Отправлено успешно'
                )
                success_count += 1
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='Не успешно',
                    server_response=str(e)
                )
                failure_count += 1

        messages.success(request, f'Рассылка отправлена: успешно {success_count}, не успешно {failure_count}')
        return redirect('mailing-list')
