from django.urls import path
from . import views

app_name = 'transports'

urlpatterns = [
    path('', views.comparator, name='comparator'),
]
