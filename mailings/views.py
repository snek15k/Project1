from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin

from clients.views import is_manager
from .models import Mailing, Client
from .forms import MailingForm
from .services import send_mailing


@login_required
def send_mailing(request):
    if request.method == 'POST':
        form = MailingForm(request.POST)
        if form.is_valid():
            mailing = form.cleaned_data['mailing']
            clients = form.cleaned_data['clients']
            send_to_all = form.cleaned_data['send_to_all']

            if send_to_all:
                clients = Client.objects.all()

            send_mailing(mailing.pk)
            return redirect('mailing_reports')
    else:
        form = MailingForm()
    return render(request, 'mailing/send_mailing.html', {'form': form})


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    @method_decorator(cache_page(60 * 5, key_prefix="mailing:list"))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        if is_manager(self.request.user):
            return Mailing.objects.all()
        else:
            return Mailing.objects.filter(owner=self.request.user)

    def get_cache_key(self):
        return f"mailing_list_{self.request.user.id}"


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_object(self, queryset=None):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        if is_manager(self.request.user) and mailing.owner != self.request.user:
             raise PermissionDenied("Менеджеры не могут редактировать чужие рассылки.")
        if not is_manager(self.request.user) and mailing.owner != self.request.user:
            raise PermissionDenied("Вы не можете редактировать эту рассылку.")
        return mailing


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_object(self, queryset=None):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['pk'])
        if is_manager(self.request.user) and mailing.owner != self.request.user:
            raise PermissionDenied("Менеджеры не могут удалять чужие рассылки.")
        if not is_manager(self.request.user) and mailing.owner != self.request.user:
            raise PermissionDenied("Вы не можете удалять эту рассылку.")
        return mailing


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
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
        mailing.is_active = False
        mailing.save()
        return redirect(reverse_lazy('mailing:mailing_list'))

