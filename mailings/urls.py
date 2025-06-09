from django.urls import path

from . import views

app_name = "mailings"

urlpatterns = [
    path("mailings/", views.MailingListView.as_view(), name="mailing_list"),
    path("mailings/create/", views.MailingCreateView.as_view(), name="mailing_create"),
    path(
        "mailings/<int:pk>/update/",
        views.MailingUpdateView.as_view(),
        name="mailing_update",
    ),
    path(
        "mailings/<int:pk>/delete/",
        views.MailingDeleteView.as_view(),
        name="mailing_delete",
    ),
    path(
        "mailings/<int:pk>/", views.MailingDetailView.as_view(), name="mailing_detail"
    ),
    path(
        "mailings/<int:pk>/deactivate/",
        views.MailingDeactivateView.as_view(),
        name="mailing_deactivate",
    ),
    path("send_mailing/", views.send_mailing, name="send_mailing"),
]
