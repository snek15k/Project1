from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

from mailings.models import Mailing
from .models import MailingLog


@login_required
def mailing_reports(request):
    user = request.user
    mailing_logs = MailingLog.objects.filter(mailing__owner=user).order_by("-date_time")
    context = {"mailing_logs": mailing_logs, "has_logs": mailing_logs.exists()}
    return render(request, "attempt/mailing_reports.html", context)


class MailingStatsView(LoginRequiredMixin, TemplateView):
    template_name = "attempt/mailing_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Общая статистика пользователя
        user_stats = MailingLog.get_user_stats(user)

        # Статистика по каждой рассылке
        mailings = Mailing.objects.filter(owner=user)
        mailing_stats = []
        for mailing in mailings:
            stats = MailingLog.get_mailing_stats(mailing)
            mailing_stats.append({"mailing": mailing, **stats})

        context.update(
            {
                "user_stats": user_stats,
                "mailing_stats": mailing_stats,
            }
        )
        return context
