from django.db import models
from django.utils import timezone
from spots.models import Lieu
from users.models import Utilisateur

class Evenement(models.Model):
    CATEGORIE_CHOICES = (
        ('Concert & Musique', 'Concert & Musique'),
        ('Art & Exposition', 'Art & Exposition'),
        ('Gastronomie & Brunch', 'Gastronomie & Brunch'),
        ('Festival & Fête', 'Festival & Fête'),
        ('Sortie Plein Air', 'Sortie Plein Air'),
    )

    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, related_name='evenements')
    titre = models.CharField(max_length=200)
    description = models.TextField()
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    image = models.CharField(max_length=500, default='https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80')
    prix = models.FloatField(default=0.0, help_text="0 si gratuit, sinon tarif en DT")
    categorie = models.CharField(max_length=50, choices=CATEGORIE_CHOICES, default='Concert & Musique')
    est_populaire = models.BooleanField(default=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='evenements_crees')

    class Meta:
        ordering = ['date_debut']

    def __str__(self):
        return f"{self.titre} @ {self.lieu.nom}"

class Partenaire(models.Model):
    TYPE_ABONNEMENT_CHOICES = (
        ('STANDARD', 'Standard (Gratuit)'),
        ('PREMIUM', 'Premium (Mise en avant + Stats)'),
        ('VIP', 'Partenaire VIP'),
    )

    nom = models.CharField(max_length=150)
    contact_nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=30)
    type_abonnement = models.CharField(max_length=20, choices=TYPE_ABONNEMENT_CHOICES, default='PREMIUM')
    date_debut = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Partenaire: {self.nom} ({self.type_abonnement})"

class OffrePromotion(models.Model):
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, related_name='offres')
    titre = models.CharField(max_length=200)
    description = models.TextField()
    code_promo = models.CharField(max_length=30, blank=True, null=True, help_text="Ex: TUNISSPOT15")
    reduction_pourcentage = models.IntegerField(default=15)
    date_debut = models.DateField(default=timezone.now)
    date_fin = models.DateField()
    est_active = models.BooleanField(default=True)
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='offres_crees')

    class Meta:
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.titre} (-{self.reduction_pourcentage}%) à {self.lieu.nom}"

class StatistiqueFiche(models.Model):
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, related_name='statistiques')
    date_stat = models.DateField(default=timezone.now)
    nombre_vues = models.IntegerField(default=0)
    nombre_clics_itineraire = models.IntegerField(default=0)
    nombre_ajouts_favoris = models.IntegerField(default=0)
    nombre_clics_menu = models.IntegerField(default=0)

    class Meta:
        unique_together = ('lieu', 'date_stat')
        ordering = ['-date_stat']

    def __str__(self):
        return f"Stats {self.lieu.nom} au {self.date_stat}"
