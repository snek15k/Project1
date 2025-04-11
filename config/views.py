from django.views.generic import TemplateView
from mailings.models import Mailing
from clients.models import Client

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailings'] = Mailing.objects.all()
        context['active_mailings'] = Mailing.objects.filter(is_active=True).count()
        context['clients'] = Client.objects.distinct().count()
        return context

home = HomeView.as_view()