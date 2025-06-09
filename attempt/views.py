from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import MailingLog


@login_required
def mailing_reports(request):
    user = request.user
    mailing_logs = MailingLog.objects.filter(mailing__owner=user).order_by("-date_time")
    context = {"mailing_logs": mailing_logs, "has_logs": mailing_logs.exists()}
    return render(request, "attempt/mailing_reports.html", context)
