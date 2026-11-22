import uuid
from django.db import models
from django.utils import timezone
from users.models import Utilisateur
from spots.models import Lieu

class ListeFavoris(models.Model):
    VISIBILITE_CHOICES = (
        ('PUBLIC', 'Public (partageable)'),
        ('PRIVE', 'Privé'),
    )
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='listes_favoris')
    nom = models.CharField(max_length=150, default='Mes coups de cœur')
    visibilite = models.CharField(max_length=20, choices=VISIBILITE_CHOICES, default='PUBLIC')
    lieux = models.ManyToManyField(Lieu, related_name='listes_ou_present', blank=True)
    date_creation = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.nom} ({self.user.username})"

    def ajouter_lieu(self, lieu):
        """Méthode ajouterLieu() définie dans le diagramme UML."""
        self.lieux.add(lieu)

    def retirer_lieu(self, lieu):
        """Méthode retirerLieu() définie dans le diagramme UML."""
        self.lieux.remove(lieu)

class Itineraire(models.Model):
    MODE_TRANSPORT_CHOICES = (
        ('MIXTE', 'Mixte (Marche + TGM / Métro)'),
        ('TGM', 'TGM & Métro uniquement'),
        ('VOITURE', 'Voiture personnelle'),
        ('TAXI', 'Taxi / VTC'),
        ('PIED', 'Tout à pied'),
    )

    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='itineraires')
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)
    budget = models.FloatField(default=50.0, help_text="Budget prévisionnel en Dinars Tunisiens")
    duree_totale = models.IntegerField(default=180, help_text="Durée totale estimée en minutes")
    mode_transport = models.CharField(max_length=30, choices=MODE_TRANSPORT_CHOICES, default='MIXTE')
    lien_partage = models.CharField(max_length=64, unique=True, blank=True)
    est_public = models.BooleanField(default=True)
    date_creation = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_creation']

    def save(self, *args, **kwargs):
        if not self.lien_partage:
            self.lien_partage = uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titre} - {self.user.username}"

    def generer_programme(self):
        """Méthode genererProgramme() définie dans le diagramme UML."""
        return list(self.etapes.order_by('ordre'))

    def partager(self):
        """Méthode partager() définie dans le diagramme UML."""
        return f"/itineraires/partage/{self.lien_partage}/"

class Etape(models.Model):
    MODE_CHOICES = (
        ('PIED', 'À pied'),
        ('TGM', 'TGM / Métro'),
        ('TAXI', 'Taxi / VTC'),
        ('VOITURE', 'Voiture'),
    )
    itineraire = models.ForeignKey(Itineraire, on_delete=models.CASCADE, related_name='etapes')
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, related_name='etapes_itineraire')
    ordre = models.IntegerField(default=1)
    heure_arrivee = models.TimeField(blank=True, null=True)
    duree_visite = models.IntegerField(default=60, help_text="Durée passée sur place en minutes")
    mode_transport = models.CharField(max_length=20, choices=MODE_CHOICES, default='PIED')
    duree_trajet = models.IntegerField(default=15, help_text="Durée de trajet depuis l'étape précédente en minutes")
    distance = models.FloatField(default=1.5, help_text="Distance en km")
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['itineraire', 'ordre']

    def __str__(self):
        return f"Étape {self.ordre}: {self.lieu.nom} ({self.itineraire.titre})"

    def calculer_trajet(self):
        """Méthode calculerTrajet() définie dans le diagramme UML."""
        return {
            'distance_km': self.distance,
            'duree_minutes': self.duree_trajet,
            'mode_transport': self.mode_transport
        }

class SortieGroupe(models.Model):
    STATUT_CHOICES = (
        ('EN_VOTE', 'En cours de vote'),
        ('VALIDEE', 'Validée'),
        ('TERMINEE', 'Terminée'),
    )
    titre = models.CharField(max_length=200)
    createur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='sorties_creees')
    date_sortie = models.DateField()
    description = models.TextField(blank=True, null=True)
    code_invitation = models.CharField(max_length=20, unique=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_VOTE')
    date_creation = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.code_invitation:
            self.code_invitation = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sortie: {self.titre} ({self.date_sortie})"

class PropositionLieu(models.Model):
    sortie = models.ForeignKey(SortieGroupe, on_delete=models.CASCADE, related_name='propositions')
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE)
    propose_par = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    commentaire = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.lieu.nom} proposé pour {self.sortie.titre}"

class Vote(models.Model):
    proposition = models.ForeignKey(PropositionLieu, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    vote_pour = models.BooleanField(default=True)

    class Meta:
        unique_together = ('proposition', 'user')

    def __str__(self):
        return f"{self.user.username} - {'+1' if self.vote_pour else '-1'}"
