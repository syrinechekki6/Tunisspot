from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('owner/', views.owner_dashboard, name='owner_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
]
