from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('evenements/', include('events.urls')),
    path('spots/', include('spots.urls')),
    path('itineraries/', include('itineraries.urls')),
    path('transports/', include('transports.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', RedirectView.as_view(url='/spots/', permanent=False)),  # Page d'accueil
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
