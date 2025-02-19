from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework.reverse import reverse_lazy

from .models import Client

class ClientListView(ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'


class ClientDetailView(DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'


class ClientCreateView(CreateView):
    model = Client
    fields = '__all__'
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')


class ClientUpdateView(UpdateView):
    model = Client
    fields = '__all__'
    template_name = 'clients/client_form.html'
    context_object_name = 'client'
    success_url = reverse_lazy('clients:client_list')


class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    context_object_name = 'client'
    success_url = reverse_lazy('clients:client_list')




