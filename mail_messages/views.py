from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework.reverse import reverse_lazy
from .models import Message


class MessageListView(ListView):
    model = Message
    queryset = Message.objects.all()
    context_object_name = 'messages'
    template_name = 'mail_messages/message_list.html'


class MessageDetailView(DetailView):
    model = Message
    context_object_name = 'message'
    template_name = 'mail_messages/message_detail.html'


class MessageCreateView(CreateView):
    model = Message
    fields = '__all__'
    template_name = 'mail_messages/message_form.html'
    success_url = reverse_lazy('mail_messages:message_list')


class MessageUpdateView(UpdateView):
    model = Message
    fields = '__all__'
    template_name = 'mail_messages/message_form.html'
    context_object_name = 'message'
    success_url = reverse_lazy('mail_messages:message_list')


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mail_messages/message_confirm_delete.html'
    context_object_name = 'message'
    success_url = reverse_lazy('mail_messages:message_list')




