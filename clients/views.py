from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

from mailings.models import Mailing
from .forms import ClientForm
from .models import Client


def is_manager(user):
    return user.groups.filter(name='Managers').exists()

class HomeView(TemplateView):
    template_name = 'clients/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            if is_manager(self.request.user):
                context['count_mailings'] = Mailing.objects.count()
                context['count_active_mailings'] = Mailing.objects.filter(is_active=True).count()
                context['unique_contacts'] = Client.objects.values('email').distinct().count()
            else:
                context['count_mailings'] = Mailing.objects.filter(owner=self.request.user).count()
                context['count_active_mailings'] = Mailing.objects.filter(owner=self.request.user, is_active=True).count()
                context['unique_contacts'] = Client.objects.filter(owner=self.request.user).distinct().count()
            return context
        else:
            return context


class AddClientView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_create.html'
    success_url = reverse_lazy('clients:client_list')

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


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'clients/client_update.html'
    success_url = reverse_lazy('clients:clients_list')
    context_object_name = 'client'

    def get_object(self, queryset=None):
        client = get_object_or_404(Client, pk=self.kwargs.get('pk'))
        if is_manager(self.request.user) and client.owner != self.request.user:
            raise PermissionDenied('Менеджеры не имеют прав на редактирование чужих получателей')
        if not is_manager(self.request.user) and client.owner != self.request.user:
            raise PermissionDenied('У вас нет прав на редактирование этого получателя')
        return client


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'clients/client_delete.html'
    success_url = reverse_lazy('clients:clients_list')

    def get_object(self, queryset=None):
        client = get_object_or_404(Client, pk=self.kwargs.get('pk'))
        if not is_manager(self.request.user) and client.owner != self.request.user:
            raise PermissionDenied('У вас нет прав на удаление этого получателя')
        if is_manager(self.request.user) and client.owner != self.request.user:
            raise PermissionDenied('Менеджеры не могут удалять чужих получателей')
        return client





