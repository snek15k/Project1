from django.urls import path
from . import views

app_name = 'mailing'

urlpatterns = [
    path('add/', views.MailingCreateView.as_view(), name='add_mailing'),
    path('', views.MailingListView.as_view(), name='mailing_list'),
    path('<int:pk>/update/', views.MailingUpdateView.as_view(), name='update_mailing'),
    path('<int:pk>/delete/', views.MailingDeleteView.as_view(), name='delete_mailing'),
]