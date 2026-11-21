from django.urls import path
from . import views

app_name = "spots"

urlpatterns = [
    path("", views.home, name="home"),
    path("spot/<slug:slug>/", views.spot_detail, name="spot_detail"),
    path("spot/<slug:slug>/menu/", views.spot_menu_detail, name="spot_menu"),
    path("spot/<int:lieu_id>/avis/nouveau/", views.avis_create, name="avis_create"),
    path("avis/<int:pk>/modifier/", views.avis_edit, name="avis_edit"),
    path("avis/<int:pk>/supprimer/", views.avis_delete, name="avis_delete"),
    path("spot/<int:lieu_id>/photos/nouvelle/", views.photo_create, name="photo_create"),
    path("photos/<int:pk>/modifier/", views.photo_edit, name="photo_edit"),
    path("photos/<int:pk>/supprimer/", views.photo_delete, name="photo_delete"),
    path("spot/<int:lieu_id>/plats/nouveau/", views.plat_create, name="plat_create"),
    path("plats/<int:pk>/modifier/", views.plat_edit, name="plat_edit"),
    path("plats/<int:pk>/supprimer/", views.plat_delete, name="plat_delete"),
]
