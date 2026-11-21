from django.contrib import admin
from .models import Categorie, Quartier, Lieu, Avis, Photo, Plat

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'slug')

@admin.register(Quartier)
class QuartierAdmin(admin.ModelAdmin):
    list_display = ('nom',)

@admin.register(Lieu)
class LieuAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'note_moyenne', 'statut')
    search_fields = ('nom',)

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
