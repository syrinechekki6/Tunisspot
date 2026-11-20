from django.contrib import admin
from .models import Categorie, Quartier, Lieu

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'slug')

@admin.register(Quartier)
class QuartierAdmin(admin.ModelAdmin):
    list_display = ('nom',)

@admin.register(Lieu)
class LieuAdmin(admin.ModelAdmin):
    list_display = ('nom', 'adresse', 'statut')
    search_fields = ('nom',)
