from django.urls import path
from . import views
from .views import AddMessageView, MessageDeleteView, MessageUpdateView, MessageListView


app_name = 'mail_messages'

urlpatterns = [
    path('', MessageListView.as_view(), name='message_list'),
    path('create/', AddMessageView.as_view(), name='message_create'),
    path('<int:pk>/edit/', MessageUpdateView.as_view(), name='message_update'),
    path('<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),
]