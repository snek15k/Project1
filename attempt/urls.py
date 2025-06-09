from django.urls import path

from . import views

app_name = "attempt"

urlpatterns = [
    path("mailing_reports/", views.mailing_reports, name="mailing_reports"),
]
