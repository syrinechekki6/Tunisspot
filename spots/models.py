from django.db import models
from django.utils.text import slugify
from django.utils import timezone


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
    """Stub minimal - requis par transports.LieuStation."""
    nom = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='lieux')
    quartier = models.ForeignKey(Quartier, on_delete=models.SET_NULL, null=True, blank=True, related_name='lieux')
    adresse = models.CharField(max_length=300, default='Tunis')
    latitude = models.FloatField(default=36.8065)
    longitude = models.FloatField(default=10.1815)
    statut = models.CharField(max_length=20, default='ACTIF')

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
