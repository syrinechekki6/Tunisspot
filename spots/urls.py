from django.urls import path
from . import views

app_name = 'spots'

urlpatterns = [
    path('', views.home, name='home'),
    path('explorer/', views.spot_list, name='spot_list'),
    path('au-hasard/', views.random_spot, name='random_spot'),
    path('nouveau/', views.spot_create, name='spot_create'),
    path('spot/<slug:slug>/', views.spot_detail, name='spot_detail'),
    path('spots/<slug:slug>/', views.spot_detail),
    path('spot/<slug:slug>/menu/', views.spot_menu_detail, name='spot_menu'),
    path('spots/<slug:slug>/menu/', views.spot_menu_detail),
    path('spot/<int:pk>/modifier/', views.spot_edit, name='spot_edit'),
    path('spots/<int:pk>/modifier/', views.spot_edit),
    path('spot/<int:pk>/supprimer/', views.spot_delete, name='spot_delete'),
    path('spots/<int:pk>/supprimer/', views.spot_delete),
    
    # Plats / Menus
    path('spot/<int:lieu_id>/plats/nouveau/', views.plat_create, name='plat_create'),
    path('plats/<int:pk>/modifier/', views.plat_edit, name='plat_edit'),
    path('plats/<int:pk>/supprimer/', views.plat_delete, name='plat_delete'),

    # Avis (CRUD complet)
    path('spot/<int:lieu_id>/avis/nouveau/', views.avis_create, name='avis_create'),
    path('avis/<int:pk>/modifier/', views.avis_edit, name='avis_edit'),
    path('avis/<int:pk>/supprimer/', views.avis_delete, name='avis_delete'),

    # Photos (CRUD complet)
    path('spot/<int:lieu_id>/photos/nouvelle/', views.photo_create, name='photo_create'),
    path('photos/<int:pk>/modifier/', views.photo_edit, name='photo_edit'),
    path('photos/<int:pk>/supprimer/', views.photo_delete, name='photo_delete'),
    
    # Revendication & Signalement
    path('spot/<int:lieu_id>/revendiquer/', views.claim_spot, name='claim_spot'),
    path('spot/<int:lieu_id>/signaler/', views.signalement_create, name='signalement_create'),
]
