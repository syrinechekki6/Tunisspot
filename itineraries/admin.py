from django.contrib import admin
from .models import ListeFavoris, Itineraire, Etape, SortieGroupe, PropositionLieu, Vote

@admin.register(ListeFavoris)
class ListeFavorisAdmin(admin.ModelAdmin):
    list_display = ('nom', 'user', 'visibilite', 'date_creation')

class EtapeInline(admin.TabularInline):
    model = Etape
    extra = 1

@admin.register(Itineraire)
class ItineraireAdmin(admin.ModelAdmin):
    list_display = ('titre', 'user', 'budget', 'duree_totale', 'mode_transport', 'est_public', 'lien_partage')
    inlines = [EtapeInline]

@admin.register(SortieGroupe)
class SortieGroupeAdmin(admin.ModelAdmin):
    list_display = ('titre', 'createur', 'date_sortie', 'code_invitation', 'statut')

@admin.register(PropositionLieu)
class PropositionLieuAdmin(admin.ModelAdmin):
    list_display = ('sortie', 'lieu', 'propose_par')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('proposition', 'user', 'vote_pour')
