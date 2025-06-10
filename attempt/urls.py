from django.urls import path

from . import views
from .views import MailingStatsView

app_name = "attempt"

urlpatterns = [
    path("mailing_reports/", views.mailing_reports, name="mailing_reports"),
    path("stats/", MailingStatsView.as_view(), name="mailing_stats")
]
