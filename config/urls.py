from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from config import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('clients.urls', namespace='clients')),
    path('mailings/', include('mailings.urls', namespace='mailings')),
    path('users/', include('users.urls', namespace='users')),
    path('mail_messages/', include('mail_messages.urls', namespace='mail_messages')),
    path('attempt/', include('attempt.urls', namespace='attempt')),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
