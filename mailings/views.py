from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework.reverse import reverse_lazy
from .models import Message, Mailing, Client


class MailingListView(ListView):
    model = Mailing
    queryset = Mailing.objects.all()
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'


class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'
    context_object_name = 'mailing'


class MailingCreateView(CreateView):
    model = Mailing
    fields = '__all__'
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')


class MailingUpdateView(UpdateView):
    model = Mailing
    fields = ['message', 'recipients', 'end_time']
    template_name = 'mailings/mailing_form.html'
    context_object_name = 'mailing'
    success_url = reverse_lazy('mailings:mailing_list')


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    context_object_name = 'mailing'
    success_url = reverse_lazy('mailings:mailing_list')






