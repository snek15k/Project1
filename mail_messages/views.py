from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from rest_framework.reverse import reverse_lazy

from .forms import MessageForm
from .models import Message
from .utils import is_manager


class AddMessageView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mail_messages/message_create.html"
    success_url = reverse_lazy("mail_messages:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.object = form.save()
        messages.success(self.request, "Сообщение создано.")
        return super().form_valid(form)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mail_messages/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        if is_manager(self.request.user):
            return Message.objects.all()
        else:
            return Message.objects.filter(owner=self.request.user)

    @method_decorator(cache_page(60, key_prefix="messages:list"))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mail_messages/message_update.html"
    success_url = reverse_lazy("mail_messages:message_list")

    def get_object(self, queryset=None):
        message = get_object_or_404(Message, pk=self.kwargs["pk"])
        if message.owner != self.request.user:
            raise PermissionDenied("Вы не можете редактировать это сообщение.")
        return message


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    template_name = "mail_messages/message_delete.html"
    success_url = reverse_lazy("mail_messages:message_list")

    def get_object(self, queryset=None):
        message = get_object_or_404(Message, pk=self.kwargs["pk"])
        if message.owner != self.request.user:
            raise PermissionDenied("Вы не можете удалять это сообщение.")
        return message


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mail_messages/message_detail.html"
    context_object_name = "message"
