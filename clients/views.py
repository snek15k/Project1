from django.http import request, HttpResponseForbidden, HttpResponseRedirect
from functools import wraps
from allauth.core.internal.httpkit import redirect
from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (CreateView, DeleteView, ListView,
                                  TemplateView, UpdateView)
from rest_framework.generics import get_object_or_404
from rest_framework.reverse import reverse_lazy, reverse

from mail_messages.utils import is_manager
from mailings.services import get_mailing_statistics

from .forms import ClientForm
from .models import Client


class HomeView(TemplateView):
    template_name = "clients/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            if is_manager(self.request.user):
                statistics = get_mailing_statistics()
            else:
                statistics = get_mailing_statistics(self.request.user)

            context["count_mailings"] = statistics["total_mailings"]
            context["count_active_mailings"] = statistics["active_mailings"]
            context["unique_contacts"] = statistics["unique_clients"]
        else:
            context["count_mailings"] = 0
            context["count_active_mailings"] = 0
            context["unique_contacts"] = 0
        return context


class AddClientView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_create.html"
    success_url = reverse_lazy("clients:client_list")

    def form_valid(self, form):
        """Присваиваем авторизованного пользователя создаваемому клиенту"""
        user = get_user(self.request)
        form.instance.owner = user
        form.instance.save()
        return super().form_valid(form)


class ListClientsView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "clients/client_list.html"
    context_object_name = "clients"

    @method_decorator(cache_page(60 * 5))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.groups.filter(name="Managers").exists():
            return Client.objects.all()
        return Client.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_manager"] = self.request.user.groups.filter(name="Managers").exists()
        return context


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_update.html"
    success_url = reverse_lazy("clients:client_list")
    context_object_name = "client"

    def get_object(self, queryset=None):
        client = get_object_or_404(Client, pk=self.kwargs.get("pk"))
        if client.owner is None:
            raise PermissionDenied("У этого получателя не установлен владелец.")
        if is_manager(self.request.user) and client.owner != self.request.user:
            raise PermissionDenied(
                "Менеджеры не имеют прав на редактирование чужих получателей"
            )
        if not is_manager(self.request.user) and client.owner != self.request.user:
            raise PermissionDenied("У вас нет прав на редактирование этого получателя")
        return client

    def form_valid(self, form):
        form.instance.save()
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "clients/client_delete.html"
    success_url = reverse_lazy("clients:clients_list")

    def get_object(self, queryset=None):
        client = get_object_or_404(Client, pk=self.kwargs.get("pk"))
        if not is_manager(self.request.user) and client.owner != self.request.user:
            raise PermissionDenied("У вас нет прав на удаление этого получателя")
        if is_manager(self.request.user) and client.owner != self.request.user:
            raise PermissionDenied("Менеджеры не могут удалять чужих получателей")
        return client
