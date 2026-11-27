from django.urls import path
from . import views

app_name = 'transports'

urlpatterns = [
    path('', views.comparator, name='comparator'),
    path('comparateur/', views.comparator),
    path('stations/nouvelle/', views.station_create, name='station_create'),
    path('stations/<int:pk>/modifier/', views.station_edit, name='station_edit'),
    path('stations/<int:pk>/supprimer/', views.station_delete, name='station_delete'),
]
