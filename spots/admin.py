from django.contrib import admin
from .models import Categorie, Quartier, Lieu, Plat, Avis, Photo, Revendication, Signalement

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'libelle_ar', 'icone', 'slug')
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

@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'lieu', 'prix', 'categorie_plat', 'est_populaire')
    list_filter = ('categorie_plat', 'est_populaire')

@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('lieu', 'user', 'note', 'type_visiteur', 'score_confiance', 'statut_moderation', 'date_publication')
    list_filter = ('statut_moderation', 'type_visiteur', 'note')

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('lieu', 'user', 'source', 'statut_moderation', 'date_ajout')
    list_filter = ('statut_moderation', 'source')

@admin.register(Revendication)
class RevendicationAdmin(admin.ModelAdmin):
    list_display = ('lieu', 'user', 'telephone_contact', 'statut', 'date_demande')
    list_filter = ('statut',)

@admin.register(Signalement)
class SignalementAdmin(admin.ModelAdmin):
    list_display = ('motif', 'lieu', 'user', 'statut', 'date_signalement')
    list_filter = ('statut', 'motif')
