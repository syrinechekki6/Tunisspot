from django.urls import path
from . import dashboard_views

app_name = 'dashboard'

urlpatterns = [
    path('admin/', dashboard_views.admin_dashboard, name='admin_dashboard'),
    path('admin/utilisateurs/', dashboard_views.admin_users, name='admin_users'),
    path('admin/utilisateurs/<int:user_id>/supprimer/', dashboard_views.admin_user_delete, name='admin_user_delete'),
    path('moderer-avis/<int:avis_id>/<str:action>/', dashboard_views.moderer_avis, name='moderer_avis'),
    path('traiter-revendication/<int:rev_id>/<str:action>/', dashboard_views.traiter_revendication, name='traiter_revendication'),
    path('valider-lieu/<int:lieu_id>/<str:action>/', dashboard_views.admin_valider_lieu, name='admin_valider_lieu'),
    path('pro/', dashboard_views.owner_dashboard, name='owner_dashboard'),
]
