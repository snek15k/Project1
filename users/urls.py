from django.contrib.auth.views import LoginView, LogoutView


from django.urls import path
from . import views
from .views import RegisterView

app_name = 'users'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('email-confirm/<str:token>/', views.EmailConfirmView.as_view(), name='email_confirm'),
    path('list/', views.UserListView.as_view(), name='user_list'),
    path('block/<int:pk>/', views.UserBlockView.as_view(), name='user_block'),
    path('unblock/<int:pk>/', views.UserUnblockView.as_view(), name='user_unblock'),
]