from django.contrib import admin
from .models import Evenement, Partenaire, OffrePromotion, StatistiqueFiche

@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('titre', 'lieu', 'date_debut', 'date_fin', 'prix', 'categorie', 'est_populaire')
    list_filter = ('categorie', 'est_populaire')

@admin.register(Partenaire)
class PartenaireAdmin(admin.ModelAdmin):
    list_display = ('nom', 'contact_nom', 'email', 'type_abonnement', 'date_debut')

@admin.register(OffrePromotion)
class OffrePromotionAdmin(admin.ModelAdmin):
    list_display = ('titre', 'lieu', 'code_promo', 'reduction_pourcentage', 'date_fin', 'est_active')
    list_filter = ('est_active',)

@admin.register(StatistiqueFiche)
class StatistiqueFicheAdmin(admin.ModelAdmin):
    list_display = ('lieu', 'date_stat', 'nombre_vues', 'nombre_clics_itineraire', 'nombre_ajouts_favoris', 'nombre_clics_menu')
