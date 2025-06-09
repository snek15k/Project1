from django.contrib.auth import views as auth_views

from django.urls import path, reverse_lazy

from .forms import LoginForm
from .views import RegisterView, VerifyEmailView, CustomPasswordResetConfirmView, CustomPasswordResetForm, \
    LoginView, LogoutView, UserBlockView, UserUnlockView, UserListView

app_name = 'users'


urlpatterns = [
    # Регистрация/авторизация
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),

    # Сброс пароля
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             form_class=CustomPasswordResetForm,
             template_name='users/registration/password_reset.html',
             success_url=reverse_lazy('users:password_reset_done')
         ),
         name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         CustomPasswordResetConfirmView.as_view(
             template_name='users/registration/password_reset_confirm.html',
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # Блокировка
    path('block/<int:pk>/', UserBlockView.as_view(), name='block_user'),
    path('unblock/<int:pk>/', UserUnlockView.as_view(), name='unblock_user'),
    path('users/', UserListView.as_view(), name='user_list'),
]