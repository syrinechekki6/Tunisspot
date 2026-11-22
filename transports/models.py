from django.db import models
from django.utils import timezone
from users.models import Utilisateur
from spots.models import Lieu

class MoyenTransport(models.Model):
    nom = models.CharField(max_length=100) # ex: Métro léger, TGM, Taxi / VTC, À pied, Voiture
    icone = models.CharField(max_length=50, default='train')
    vitesse_moyenne_kmh = models.FloatField(default=30.0)
    tarif_base_tnd = models.FloatField(default=0.5)
    tarif_km_tnd = models.FloatField(default=0.3)
    confort = models.CharField(max_length=50, default='Moyen')
    ecologique = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom

class Ligne(models.Model):
    nom = models.CharField(max_length=150) # ex: Ligne TGM Tunis Marine - La Marsa
    code = models.CharField(max_length=20) # ex: TGM, M1, M2
    couleur = models.CharField(max_length=20, default='#0ea5e9')
    moyen_transport = models.ForeignKey(MoyenTransport, on_delete=models.CASCADE, related_name='lignes')

    def __str__(self):
        return f"{self.code} - {self.nom}"

class Station(models.Model):
    TYPE_CHOICES = (
        ('TGM', 'TGM'),
        ('METRO', 'Métro léger'),
        ('BUS', 'Bus'),
        ('TRAIN', 'Train de banlieue'),
    )
    nom = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='TGM')
    ligne = models.ForeignKey(Ligne, on_delete=models.SET_NULL, null=True, blank=True, related_name='stations')
    latitude = models.FloatField(default=36.8065)
    longitude = models.FloatField(default=10.1815)
    ordre = models.IntegerField(default=1)

    class Meta:
        ordering = ['ligne', 'ordre']

    def __str__(self):
        return f"Station {self.nom} ({self.type})"

class LieuStation(models.Model):
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, related_name='dessertes')
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='lieux_proches')
    distance_metres = models.IntegerField(default=300)
    temps_marche_minutes = models.IntegerField(default=4)

    class Meta:
        unique_together = ('lieu', 'station')

    def __str__(self):
        return f"{self.lieu.nom} à {self.distance_metres}m de {self.station.nom}"

class TrajetHistorique(models.Model):
    user = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='trajets_recherches')
    depart_nom = models.CharField(max_length=200)
    depart_latitude = models.FloatField(default=36.8065)
    depart_longitude = models.FloatField(default=10.1815)
    arrivee_nom = models.CharField(max_length=200, default='Arrivée')
    arrivee_latitude = models.FloatField(default=36.8065)
    arrivee_longitude = models.FloatField(default=10.1815)
    arrivee_lieu = models.ForeignKey(Lieu, on_delete=models.SET_NULL, null=True, blank=True, related_name='trajets_vers_lieu')
    distance_km = models.FloatField()
    duree_minutes = models.IntegerField()
    mode_choisi = models.CharField(max_length=50)
    cout_estime_tnd = models.FloatField()
    date_recherche = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_recherche']

    def __str__(self):
        return f"Trajet {self.depart_nom} -> {self.arrivee_nom} ({self.mode_choisi})"
