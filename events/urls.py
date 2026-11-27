from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('nouveau/', views.event_create, name='event_create'),
    path('<int:pk>/modifier/', views.event_edit, name='event_edit'),
    path('<int:pk>/supprimer/', views.event_delete, name='event_delete'),
    
    # Offres
    path('offres/nouvelle/', views.offre_create, name='offre_create'),
    path('offres/<int:pk>/modifier/', views.offre_edit, name='offre_edit'),
    path('offres/<int:pk>/supprimer/', views.offre_delete, name='offre_delete'),
]
