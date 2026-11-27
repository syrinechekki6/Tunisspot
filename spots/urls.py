from django.urls import path
from . import views

app_name = "spots"
urlpatterns = [
    path("", views.home, name="home"),
]
