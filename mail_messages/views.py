from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework.reverse import reverse_lazy
from .forms import MessageForm
from .models import Message


class AddMessageView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'add_message.html'
    success_url = reverse_lazy('mail_messages:message_list')


class MessageListView(ListView):
    model = Message
    template_name = 'mail_messages/message_list.html'
    context_object_name = 'messages'


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'message_detail.html'
    success_url = reverse_lazy('mail_messages:message_list')


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'message_delete.html'
    success_url = reverse_lazy('mail_messages:message_list')



