from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('transports/', include('transports.urls')),
    path('itineraires/', include('itineraries.urls')),
    path('evenements/', include('events.urls')),
    path('users/', include('users.urls')),
    path('dashboard/', include('spots.dashboard_urls')),
    path('', include('spots.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
