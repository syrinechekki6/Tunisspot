from django.urls import path
from . import views

app_name = 'itineraries'

urlpatterns = [
    path('', views.itinerary_list, name='itinerary_list'),
    path('generateur/', views.generator, name='generator'),
    path('creer/', views.itinerary_create, name='itinerary_create'),
    path('<int:pk>/modifier/', views.itinerary_edit, name='itinerary_edit'),
    path('<int:pk>/supprimer/', views.itinerary_delete, name='itinerary_delete'),
    path('creer-avec/<int:spot_id>/', views.create_with_spot, name='create_with_spot'),
    path('mes-itineraires/', views.my_itineraries, name='my_itineraries'),
    path('partage/<str:lien_partage>/', views.itinerary_detail, name='itinerary_detail'),
    path('<int:itineraire_id>/etapes/ajouter/', views.etape_add, name='etape_add'),
    path('etapes/<int:pk>/supprimer/', views.etape_delete, name='etape_delete'),
    
    # Favoris
    path('favoris/', views.favoris, name='favoris'),
    path('favoris/toggle/<int:spot_id>/', views.toggle_favorite, name='toggle_favorite'),

    # Sorties de Groupe
    path('groupes/', views.group_trips, name='group_trips'),
    path('groupes/<str:code>/', views.group_trip_detail, name='group_trip_detail'),
    path('propositions/<int:prop_id>/voter/', views.vote_proposition, name='vote_proposition'),
]
