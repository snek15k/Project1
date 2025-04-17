from tempfile import template

from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views

from django.urls import path
from . import views
from .views import RegisterView, profile_view, CustomPasswordResetView, CustomPasswordResetConfirmView

app_name = 'users'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='users/registration/login.html'), name='login'),
    path('register/', views.RegisterView.as_view(template_name='users/registration/register.html'), name='register'),
    path('logout/', LogoutView.as_view(next_page='users:login'), name='logout'),
    path('email-confirm/<str:token>/', views.EmailConfirmView.as_view(), name='email_confirm'),
    path('list/', views.UserListView.as_view(template_name='users/user_list.html'), name='user_list'),
    path('block/<int:pk>/', views.UserBlockView.as_view(), name='user_block'),
    path('unblock/<int:pk>/', views.UserUnblockView.as_view(), name='user_unblock'),
    path('profile/', profile_view, name='profile'),
    path('password_reset/', CustomPasswordResetView.as_view(template_name='users/registration/password_reset.html'), name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='users/registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(template_name='users/registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='users/registration/password_reset_complete.html'),
         name='password_reset_complete'),
]