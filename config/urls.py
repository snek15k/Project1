from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from config import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clients/', include('clients.urls', namespace='clients')),
    path('', views.home, name='home'),
    path('accounts/', include('allauth.urls')),
    #path('mailings/', include(('mailings.urls', 'mailings'), namespace='mailings')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
