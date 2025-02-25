from django.urls import path
from . import views
from .views import AddMessageView, MessageDeleteView, MessageUpdateView, MessageListView


app_name = 'mail_messages'

urlpatterns = [
    path('add/', views.AddMessageView.as_view(), name='add_message'),
    path('', views.MessageListView.as_view(), name='message_list'),
    path('<int:pk>/update/', views.MessageUpdateView.as_view(), name='update_message'),
    path('<int:pk>/delete/', views.MessageDeleteView.as_view(), name='delete_message'),
]