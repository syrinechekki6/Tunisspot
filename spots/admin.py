from django.contrib import admin
from .models import Categorie, Quartier, Lieu, Revendication, Signalement

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'icone', 'slug')
    prepopulated_fields = {'slug': ('libelle',)}

@admin.register(Quartier)
class QuartierAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ville', 'latitude', 'longitude')

@admin.register(Lieu)
class LieuAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'quartier', 'fourchette_prix', 'note_moyenne', 'est_pepite_locale', 'statut')
    list_filter = ('categorie', 'quartier', 'fourchette_prix', 'est_pepite_locale', 'statut')
    search_fields = ('nom', 'description', 'adresse')
    prepopulated_fields = {'slug': ('nom',)}

@admin.register(Revendication)
class RevendicationAdmin(admin.ModelAdmin):
    list_display = ('lieu', 'user', 'telephone_contact', 'statut', 'date_demande')
    list_filter = ('statut',)

@admin.register(Signalement)
class SignalementAdmin(admin.ModelAdmin):
    list_display = ('motif', 'lieu', 'user', 'statut', 'date_signalement')
    list_filter = ('statut', 'motif')
