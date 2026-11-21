from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from users.models import Utilisateur


class Categorie(models.Model):
    libelle = models.CharField(max_length=100, unique=True)
    libelle_ar = models.CharField(max_length=100, blank=True, null=True)
    libelle_en = models.CharField(max_length=100, blank=True, null=True)
    icone = models.CharField(max_length=50, default='fa-utensils')
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    image_couverture = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['libelle']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.libelle)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.libelle


class Quartier(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    ville = models.CharField(max_length=100, default='Grand Tunis')
    latitude = models.FloatField(default=36.8065)
    longitude = models.FloatField(default=10.1815)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Lieu(models.Model):
    PRIX_CHOICES = (
        ('E', 'Economique (< 15 DT)'),
        ('EE', 'Moyen (15 - 40 DT)'),
        ('EEE', 'Haut de gamme (> 40 DT)'),
    )
    STATUT_CHOICES = (
        ('ACTIF', 'Actif'),
        ('EN_ATTENTE', 'En attente de validation'),
        ('FERME', 'Ferme temporairement'),
    )
    FOULE_CHOICES = (
        ('Faible', 'Calme'),
        ('Moyen', 'Affluence moderee'),
        ('Eleve', 'Tres frequente'),
    )

    place_id = models.CharField(max_length=150, blank=True, null=True, unique=True)
    nom = models.CharField(max_length=200, verbose_name="Nom de l etablissement")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='lieux')
    quartier = models.ForeignKey(Quartier, on_delete=models.SET_NULL, null=True, blank=True, related_name='lieux')
    adresse = models.CharField(max_length=300)
    latitude = models.FloatField(default=36.8065)
    longitude = models.FloatField(default=10.1815)
    telephone = models.CharField(max_length=50, blank=True, null=True)
    site_web = models.URLField(max_length=300, blank=True, null=True)
    fourchette_prix = models.CharField(max_length=5, choices=PRIX_CHOICES, default='EE')
    prix_moyen = models.FloatField(default=25.0)
    horaires = models.CharField(max_length=255, default='Tous les jours de 08:00 a 23:00')
    description = models.TextField(blank=True, null=True)
    image_principale = models.CharField(max_length=500, default='https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80')
    note_moyenne = models.FloatField(default=4.5)
    nombre_avis = models.IntegerField(default=0)
    est_pepite_locale = models.BooleanField(default=False)
    indice_foule = models.CharField(max_length=20, choices=FOULE_CHOICES, default='Moyen')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF')
    wifi = models.BooleanField(default=True)
    terrasse = models.BooleanField(default=True)
    parking = models.BooleanField(default=False)
    acces_pmr = models.BooleanField(default=True)
    vue_mer = models.BooleanField(default=False)
    climatisation = models.BooleanField(default=True)
    ambiance_romantique = models.BooleanField(default=False)
    ambiance_famille = models.BooleanField(default=True)
    ambiance_amis = models.BooleanField(default=True)
    halal = models.BooleanField(default=True)
    vegetarien = models.BooleanField(default=False)
    proprietaire = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='etablissements_geres')
    date_creation = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-note_moyenne', '-date_creation']
        verbose_name_plural = "Lieux"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nom)
            slug = base_slug
            c = 1
            while Lieu.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{c}"
                c += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} ({self.quartier.nom if self.quartier else 'Tunis'})"

    @property
    def est_ouvert(self):
        return True


class Revendication(models.Model):
    STATUT_CHOICES = (
        ('EN_ATTENTE', 'En attente'),
        ('APPROUVEE', 'Approuvee'),
        ('REJETEE', 'Rejetee'),
    )
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, related_name='revendications')
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='revendications')
    justificatif = models.TextField()
    telephone_contact = models.CharField(max_length=30)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    date_demande = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Revendication de {self.user.username} pour {self.lieu.nom}"


class Signalement(models.Model):
    STATUT_CHOICES = (
        ('NOUVEAU', 'Nouveau'),
        ('EN_COURS', "En cours d examen"),
        ('RESOLU', 'Resolu'),
        ('REJETE', 'Rejete'),
    )
    MOTIF_CHOICES = (
        ('FERME', 'Etablissement ferme definitivement'),
        ('INFO_FAUSSE', 'Informations ou horaires incorrects'),
        ('SPAM_AVIS', 'Avis faux ou abusif'),
        ('PHOTO_INAPPROPRIEE', 'Photo inappropriee'),
        ('AUTRE', 'Autre signalement'),
    )
    user = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='signalements')
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, null=True, blank=True, related_name='signalements')
    motif = models.CharField(max_length=30, choices=MOTIF_CHOICES)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='NOUVEAU')
    date_signalement = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Signalement #{self.id} ({self.get_motif_display()})"
