from django.urls import path
from . import views
from .views import AddClientView, ClientDeleteView, ClientUpdateView, ListClientsView, ClientForm


app_name = 'clients'

urlpatterns = [
    path('', views.home, name='home'),
    path('clients/', ListClientsView.as_view(), name='client_list'),
    path('create/', AddClientView.as_view(), name='client_create'),
    path('update/<int:pk>/', ClientUpdateView.as_view(), name='client_update'),
    path('delete/<int:pk>/', ClientDeleteView.as_view(), name='client_delete'),
]
