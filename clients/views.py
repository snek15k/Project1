from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from rest_framework.reverse import reverse_lazy
from .forms import ClientForm
from .models import Client


class AddClientView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/add_client.html'
    success_url = reverse_lazy('clients:clients')


class ListClientsView(ListView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/list_clients.html'
    context_object_name = 'clients'


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/detail_client.html'
    success_url = reverse_lazy('clients:clients')


class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:clients')









