from django.urls import path
from . import views

app_name = "spots"
urlpatterns = [
    path("", views.home, name="home"),
    path("liste/", views.spot_list, name="spot_list"),
    path("aleatoire/", views.random_spot, name="random_spot"),
    path("nouveau/", views.spot_create, name="spot_create"),
]
