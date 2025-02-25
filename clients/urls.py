from django.urls import path
from . import views
from .views import AddClientView, ClientDeleteView, ClientUpdateView, ListClientsView, ClientForm


app_name = 'clients'

urlpatterns = [
    path('add/', views.AddClientView.as_view(), name='add_client'),
    path('', views.ListClientsView.as_view(), name='clients'),
    path('<int:pk>/update/', views.ClientUpdateView.as_view(), name='update_client'),
    path('<int:pk>/delete/', views.ClientDeleteView.as_view(), name='delete_client'),
]