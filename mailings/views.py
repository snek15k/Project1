from pyexpat.errors import messages

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)
from rest_framework.exceptions import PermissionDenied

from clients.models import Client
from clients.views import is_manager
from mailings.models import Mailing

from .forms import MailingForm
from .models import Client, Mailing
from .services import get_mailing_statistics, send_mailing


@login_required
def send_mailing(request):
    if request.method == "POST":
        form = MailingForm(request.POST)
        if form.is_valid():
            try:
                mailing = form.cleaned_data["mailing"]
                successful = send_mailing(mailing.pk)
                messages.success(
                    request, f"Рассылка отправлена. Успешных отправок: {successful}"
                )
            except ValidationError as e:
                messages.error(request, str(e))
            return redirect("mailing_reports")
    else:
        form = MailingForm()
    return render(request, "mailing/send_mailing.html", {"form": form})


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailings/mailing_list.html"
    context_object_name = "mailings"

    @method_decorator(cache_page(60, key_prefix="mailing:list"))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        if is_manager(self.request.user):
            return Mailing.objects.all()
        else:
            return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if is_manager(self.request.user):
            statistics = get_mailing_statistics()
        else:
            statistics = get_mailing_statistics(self.request.user)

        context["total_mailings"] = statistics["total_mailings"]
        context["active_mailings"] = statistics["active_mailings"]
        context["unique_clients"] = statistics["unique_clients"]

        return context


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailings/mailing_form.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_object(self, queryset=None):
        mailing = get_object_or_404(Mailing, pk=self.kwargs["pk"])
        if mailing.owner != self.request.user and not is_manager(self.request.user):
            raise PermissionDenied("Вы не можете редактировать эту рассылку.")
        return mailing


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = "mailings/mailing_delete.html"
    success_url = reverse_lazy("mailings:mailing_list")

    def get_object(self, queryset=None):
        mailing = get_object_or_404(Mailing, pk=self.kwargs["pk"])
        if mailing.owner != self.request.user and not is_manager(self.request.user):
            raise PermissionDenied("Вы не можете удалять эту рассылку.")
        return mailing


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailings/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        mailing = get_object_or_404(Mailing, pk=self.kwargs["pk"])
        if not is_manager(self.request.user) and mailing.owner != self.request.user:
            raise PermissionDenied("Вы не можете просматривать детали этой рассылки.")
        return mailing


class MailingDeactivateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        if not is_manager(request.user):
            raise PermissionDenied("Только менеджеры могут деактивировать рассылки.")

        mailing = get_object_or_404(Mailing, pk=pk)
        return render(
            request, "mailings/mailing_deactivate_mailing.html", {"mailing": mailing}
        )

    def post(self, request, pk):
        if not is_manager(request.user):
            raise PermissionDenied("Только менеджеры могут деактивировать рассылки")

        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.is_active = False
        mailing.save()
        messages.success(request, f"Рассылка '{mailing.name}' успешно деактивирована")
        return redirect("mailings:mailing_list")
