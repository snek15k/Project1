from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import MailingLog

@login_required
def mailing_reports(request):
    user = request.user
    mailing_logs = MailingLog.objects.filter(mailing__created_by=user).order_by('-date_time')
    context = {
        'mailing_logs': mailing_logs
    }
    return render(request, 'attempt/mailing_reports.html', context)
