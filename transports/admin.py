from django.contrib import admin
from .models import MoyenTransport, Ligne, Station, LieuStation, TrajetHistorique

@admin.register(MoyenTransport)
class MoyenTransportAdmin(admin.ModelAdmin):
    list_display = ('nom', 'vitesse_moyenne_kmh', 'tarif_base_tnd', 'tarif_km_tnd', 'confort', 'ecologique')

@admin.register(Ligne)
class LigneAdmin(admin.ModelAdmin):
    list_display = ('code', 'nom', 'moyen_transport', 'couleur')

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type', 'ligne', 'ordre', 'latitude', 'longitude')
    list_filter = ('type', 'ligne')

@admin.register(LieuStation)
class LieuStationAdmin(admin.ModelAdmin):
    list_display = ('lieu', 'station', 'distance_metres', 'temps_marche_minutes')

@admin.register(TrajetHistorique)
class TrajetHistoriqueAdmin(admin.ModelAdmin):
    list_display = ('user', 'depart_nom', 'arrivee_lieu', 'distance_km', 'duree_minutes', 'mode_choisi', 'date_recherche')
