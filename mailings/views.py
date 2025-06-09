from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from pyexpat.errors import messages
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin

from clients.views import is_manager
from .models import Mailing, Client
from .forms import MailingForm
from .services import send_mailing
from mailings.models import Mailing
from clients.models import Client


@login_required
def send_mailing(request):
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            try:
                mailing = form.cleaned_data['mailing']
                successful = send_mailing(mailing.pk)
                messages.success(request, f"Рассылка отправлена. Успешных отправок: {successful}")
            except ValidationError as e:
                messages.error(request, str(e))
            return redirect('mailing_reports')
    else:
        form = MailingForm()
    return render(request, 'mailing/send_mailing.html', {'form': form})


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'

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

        mailings = self.get_queryset()
        total_mailings = mailings.count()
        active_mailings_count = mailings.filter(is_active=True).count()
        unique_clients = Client.objects.distinct().count()

        context['total_mailings'] = total_mailings
        context['active_mailings'] = active_mailings_count
        context['unique_clients'] = unique_clients
        return context



class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_object(self, queryset=None):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        if mailing.owner != self.request.user and not is_manager(self.request.user):
            raise PermissionDenied("Вы не можете редактировать эту рассылку.")
        return mailing


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def get_object(self, queryset=None):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        if mailing.owner != self.request.user and not is_manager(self.request.user):
            raise PermissionDenied("Вы не можете удалять эту рассылку.")
        return mailing


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'
    context_object_name = 'mailing'

    def get_object(self, queryset=None):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        if not is_manager(self.request.user) and mailing.owner != self.request.user:
            raise PermissionDenied("Вы не можете просматривать детали этой рассылки.")
        return mailing


class MailingDeactivateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        if not is_manager(request.user):
            raise PermissionDenied("Только менеджеры могут деактивировать рассылки.")

        mailing = get_object_or_404(Mailing, pk=pk)
        return render(request, 'mailings/mailing_deactivate_mailing.html', {'mailing': mailing})

    def post(self, request, pk):
        if not is_manager(request.user):
            raise PermissionDenied("Только менеджеры могут деактивировать рассылки")

        mailing = get_object_or_404(Mailing, pk=pk)
        mailing.is_active = False
        mailing.save()
        messages.success(request, f"Рассылка '{mailing.name}' успешно деактивирована")
        return redirect('mailings:mailing_list')

