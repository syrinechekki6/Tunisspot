from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from users.models import Utilisateur


# ----- STUBS LIEUX (dependance) -----
class Categorie(models.Model):
    libelle = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.libelle)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.libelle


class Quartier(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nom


class Lieu(models.Model):
    """Stub minimal de Lieu pour les cles etrangeres Avis, Photo, Plat."""
    nom = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='lieux')
    quartier = models.ForeignKey(Quartier, on_delete=models.SET_NULL, null=True, blank=True, related_name='lieux')
    adresse = models.CharField(max_length=300, default='Tunis')
    note_moyenne = models.FloatField(default=4.5)
    nombre_avis = models.IntegerField(default=0)
    est_pepite_locale = models.BooleanField(default=False)
    statut = models.CharField(max_length=20, default='ACTIF')
    date_creation = models.DateTimeField(default=timezone.now)

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
        return self.nom

    def calculer_note_moyenne(self):
        avis_approuves = self.avis.filter(statut_moderation='APPROUVE')
        if avis_approuves.exists():
            total_points = sum(a.note * a.score_confiance for a in avis_approuves)
            total_weights = sum(a.score_confiance for a in avis_approuves)
            self.note_moyenne = round(total_points / total_weights, 1) if total_weights > 0 else 4.0
            self.nombre_avis = avis_approuves.count()
            residents_avis = avis_approuves.filter(type_visiteur='RESIDENT')
            if avis_approuves.count() >= 2 and residents_avis.count() / avis_approuves.count() >= 0.6 and self.note_moyenne >= 4.3:
                self.est_pepite_locale = True
            self.save(update_fields=['note_moyenne', 'nombre_avis', 'est_pepite_locale'])
        return self.note_moyenne


# ----- AVIS -----
class Avis(models.Model):
    TYPE_VISITEUR_CHOICES = (
        ('RESIDENT', 'Resident Tunisien'),
        ('TOURISTE', 'Touriste'),
        ('ANONYME', 'Anonyme'),
    )
    STATUT_CHOICES = (
        ('APPROUVE', 'Approuve'),
        ('EN_ATTENTE', 'En attente'),
        ('REJETE', 'Rejete'),
    )

    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, related_name='avis')
    user = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='avis')
    note = models.IntegerField(default=4)
    commentaire = models.TextField()
    date_publication = models.DateTimeField(default=timezone.now)
    type_visiteur = models.CharField(max_length=20, choices=TYPE_VISITEUR_CHOICES, default='ANONYME')
    score_confiance = models.FloatField(default=1.0)
    statut_moderation = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')

    class Meta:
        ordering = ['-date_publication']

    def __str__(self):
        return f"Avis {self.note}/5 sur {self.lieu.nom}"

    def save(self, *args, **kwargs):
        if self.user:
            self.score_confiance = getattr(self.user, 'niveau_confiance', 1.0)
            if self.user.role == 'RESIDENT':
                self.type_visiteur = 'RESIDENT'
            elif self.user.role == 'TOURISTE':
                self.type_visiteur = 'TOURISTE'
        super().save(*args, **kwargs)
        self.lieu.calculer_note_moyenne()

    def soumettre(self):
        self.statut_moderation = 'EN_ATTENTE'
        self.save()

    def approuver(self):
        self.statut_moderation = 'APPROUVE'
        self.save(update_fields=['statut_moderation'])
        self.lieu.calculer_note_moyenne()

    def rejeter(self):
        self.statut_moderation = 'REJETE'
        self.save(update_fields=['statut_moderation'])
        self.lieu.calculer_note_moyenne()


# ----- PHOTO -----
class Photo(models.Model):
    STATUT_CHOICES = (
        ('APPROUVE', 'Approuve'),
        ('EN_ATTENTE', 'En attente'),
        ('REJETE', 'Rejete'),
    )
    SOURCE_CHOICES = (
        ('COMMUNAUTE', 'Communaute'),
        ('PROPRIETAIRE', 'Proprietaire'),
        ('GOOGLE', 'Google Places'),
    )

    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, related_name='photos')
    user = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='photos')
    url = models.CharField(max_length=500)
    legende = models.CharField(max_length=200, blank=True, null=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='COMMUNAUTE')
    statut_moderation = models.CharField(max_length=20, choices=STATUT_CHOICES, default='APPROUVE')
    date_ajout = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Photo {self.id} de {self.lieu.nom}"

    def approuver(self):
        self.statut_moderation = 'APPROUVE'
        self.save(update_fields=['statut_moderation'])

    def rejeter(self):
        self.statut_moderation = 'REJETE'
        self.save(update_fields=['statut_moderation'])


# ----- PLAT / MENU -----
class Plat(models.Model):
    CATEGORIE_PLAT_CHOICES = (
        ('Entree', 'Entree / Salade'),
        ('Plat principal', 'Plat principal'),
        ('Dessert', 'Dessert & Patisserie'),
        ('Boisson', 'Boisson & Cafe'),
        ('Specialite Tunisienne', 'Specialite Tunisienne'),
    )

    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, related_name='plats')
    nom = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    prix = models.FloatField(help_text="Prix en DT")
    categorie_plat = models.CharField(max_length=50, choices=CATEGORIE_PLAT_CHOICES, default='Plat principal')
    photo = models.CharField(max_length=500, blank=True, null=True)
    est_populaire = models.BooleanField(default=False)

    class Meta:
        ordering = ['categorie_plat', 'prix']

    def __str__(self):
        return f"{self.nom} - {self.prix} DT ({self.lieu.nom})"
