from django.urls import path
from . import views

app_name = 'itineraries'

urlpatterns = [
    path('', views.generator, name='generator'),
    path('favoris/', views.favoris, name='favoris'),
    path('mes-itineraires/', views.my_itineraries, name='my_itineraries'),
    path('voyages-groupe/', views.group_trips, name='group_trips'),
]
