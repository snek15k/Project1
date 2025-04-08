from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from urllib3 import request

from .forms import ClientForm
from .models import Client


def is_manager(user):
    return user.groups.filter(name='Managers').exists()


class AddClientView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/add_client.html'
    success_url = reverse_lazy('clients:clients')

    def form_valid(self, form):
        """Присваиваем авторизованного пользователя создаваемому клиенту"""
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ListClientsView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        if is_manager(self.request.user):
            queryset = Client.objects.all()
        else:
            queryset = Client.objects.filter(owner=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['clients'] = page_obj
        return context

    @method_decorator(cache_page(60 * 5, key_prefix='client_list'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_cache_key(self):
        return f'{self.request.user.id}_clients_list'


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_form.html'
    success_url = reverse_lazy('clients:clients')
    context_object_name = 'client'

    def get_object(self, queryset=None):
        client = get_object_or_404(Client, pk=self.kwargs.get('pk'))
        if not is_manager(self.request.user) and client.owner != self.request.user:
            raise PermissionDenied('Отсутствуют права на редактирование этого получателя')
        return client

    def dispatch(self, request, *args, **kwargs):
        client = self.get_object()
        if is_manager(request.user) and client.owner != request.user:
            return HttpResponseRedirect('Менеджеры не имеют прав на редактирование чужих пользователей')
        return super().dispatch(request, *args, **kwargs)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:clients')

    def get_object(self, queryset=None):
        client = get_object_or_404(Client, pk=self.kwargs.get('pk'))
        if not is_manager(self.request.user) and client.owner != self.request.user:
            raise PermissionDenied('У вас нет прав на удаление этого получателя')
        return client

    def dispatch(self, request, *args, **kwargs):
        client = self.get_object()
        if is_manager(request.user) and client.owner != request.user:
            return HttpResponseForbidden('Менеджеры не могут удалять чужих получателей')
        return super().dispatch(request, *args, **kwargs)









