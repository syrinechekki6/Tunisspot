from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Preference, Badge, UserBadge, Notification

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'nom', 'email', 'role', 'langue', 'points', 'est_guide_local', 'is_staff')
    list_filter = ('role', 'langue', 'est_guide_local', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations TunisSpot', {'fields': ('nom', 'telephone', 'langue', 'role', 'avatar_url', 'points', 'niveau_confiance', 'est_guide_local')}),
    )

@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'budget_max', 'ambiances', 'regimes')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'points_requis', 'icone')

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'date_obtention')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'titre', 'date_envoi', 'est_lue')
    list_filter = ('est_lue',)
