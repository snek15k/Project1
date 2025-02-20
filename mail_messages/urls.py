from django.urls import path
from .views import MessageListView, MessageCreateView, MessageDeleteView, MessageDetailView, MessageUpdateView


app_name = 'mail_messages'

urlpatterns = [
    path('', MessageListView.as_view(), name='message_list'),
    path('message/create/', MessageCreateView.as_view(), name='mail_message_create'),
    path('<int:pk>/', MessageDetailView.as_view(), name='mail_message_detail'),
    path('<int:pk>/delete/', MessageDeleteView.as_view(), name='mail_message_delete'),
    path('<int:pk>/update/', MessageUpdateView.as_view(), name='mail_message_update'),
]