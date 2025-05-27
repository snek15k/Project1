from django.contrib.auth import views as auth_views

from django.urls import path, reverse_lazy

from .forms import LoginForm
from .views import RegisterView, VerifyEmailView, ProfileView, CustomPasswordResetConfirmView, CustomPasswordResetForm, \
    ProfileEditView, LoginView, LogoutView

app_name = 'users'


urlpatterns = [
    # Регистрация/авторизация
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),

    # Профиль
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile-edit'),

    # Сброс пароля
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             form_class=CustomPasswordResetForm,
             template_name='users/registration/password_reset.html',
             email_template_name='users/registration/password_reset_email.html',
             success_url=reverse_lazy('users:password_reset_done')
         ),
         name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]