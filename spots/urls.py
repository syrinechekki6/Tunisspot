from django.urls import path
from . import views

app_name = "spots"

urlpatterns = [
    path("", views.home, name="home"),
    path("explorer/", views.spot_list, name="spot_list"),
    path("au-hasard/", views.random_spot, name="random_spot"),
    path("nouveau/", views.spot_create, name="spot_create"),
    path("spot/<slug:slug>/", views.spot_detail, name="spot_detail"),
    path("spots/<slug:slug>/", views.spot_detail),
    path("spot/<int:pk>/modifier/", views.spot_edit, name="spot_edit"),
    path("spots/<int:pk>/modifier/", views.spot_edit),
    path("spot/<int:pk>/supprimer/", views.spot_delete, name="spot_delete"),
    path("spots/<int:pk>/supprimer/", views.spot_delete),
    path("spot/<int:lieu_id>/revendiquer/", views.claim_spot, name="claim_spot"),
    path("spot/<int:lieu_id>/signaler/", views.signalement_create, name="signalement_create"),
]
