from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Utilisateur(AbstractUser):
    ROLE_CHOICES = (
        ('VISITEUR', 'Visiteur'),
        ('PROPRIETAIRE', 'Établissement'),
        ('ADMIN', 'Administrateur'),
        ('TOURISTE', 'Visiteur (Touriste)'),
        ('RESIDENT', 'Visiteur (Résident)'),
        ('MODERATEUR', 'Modérateur'),
    )
    LANGUE_CHOICES = (
        ('FR', 'Français'),
        ('EN', 'English'),
        ('AR', 'العربية'),
    )

    nom = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nom complet")
    telephone = models.CharField(max_length=30, blank=True, null=True, verbose_name="Numéro de téléphone")
    langue = models.CharField(max_length=5, choices=LANGUE_CHOICES, default='FR', verbose_name="Langue préférée")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='VISITEUR', verbose_name="Rôle utilisateur")
    avatar_url = models.CharField(max_length=500, blank=True, null=True, default='')
    photo_profil = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Photo de profil")
    points = models.IntegerField(default=50, verbose_name="Points de découverte")
    niveau_confiance = models.FloatField(default=1.0, verbose_name="Score de confiance utilisateur")
    est_guide_local = models.BooleanField(default=False, verbose_name="Badge Guide Local Certifié")
    date_inscription = models.DateTimeField(default=timezone.now, verbose_name="Date d'inscription")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def signaler_avis(self, avis, motif, description=""):
        """Méthode signalerAvis() définie dans le diagramme de classes UML."""
        from spots.models import Signalement
        return Signalement.objects.create(user=self, avis=avis, lieu=avis.lieu, motif=motif, description=description)

    @property
    def has_custom_avatar(self):
        return bool(self.photo_profil or (self.avatar_url and self.avatar_url.strip()))

    @property
    def avatar_display(self):
        if self.photo_profil:
            return self.photo_profil.url
        if self.avatar_url and self.avatar_url.strip():
            return self.avatar_url
        return None

    def save(self, *args, **kwargs):
        if not self.nom and (self.first_name or self.last_name):
            self.nom = f"{self.first_name} {self.last_name}".strip()
        super().save(*args, **kwargs)

    @property
    def titre_explorateur(self):
        if self.points >= 500:
            return "Ambassadeur de Tunis"
        elif self.points >= 250:
            return "Guide Local d'Élite"
        elif self.points >= 100:
            return "Explorateur Avancé"
        return "Nouveau Curieux"

class Preference(models.Model):
    user = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='preference')
    budget_max = models.FloatField(default=100.0, verbose_name="Budget max habituel (DT)")
    ambiances = models.CharField(max_length=255, default='romantique,terrasse,calme', help_text="Comma-separated: romantique,terrasse,famille,amis,etudiant,vue_mer")
    regimes = models.CharField(max_length=255, default='halal', help_text="Comma-separated: halal,vegetarien,sans_gluten")

    def enregistrer(self):
        """Méthode métier enregistrer() définie dans le diagramme de classes."""
        self.save()

    def __str__(self):
        return f"Préférences de {self.user.username}"

class Badge(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    icone = models.CharField(max_length=50, default='award') # FontAwesome
    points_requis = models.IntegerField(default=100)

    def __str__(self):
        return self.nom

class UserBadge(models.Model):
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_obtention = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} - {self.badge.nom}"

class Notification(models.Model):
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='notifications')
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lien = models.CharField(max_length=255, blank=True, null=True)
    date_envoi = models.DateTimeField(default=timezone.now)
    est_lue = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_envoi']

    def __str__(self):
        return f"{self.titre} pour {self.user.username}"

    def marquer_comme_lue(self):
        """Méthode marquerCommeLue() définie dans le diagramme UML."""
        self.est_lue = True
        self.save(update_fields=['est_lue'])

    @classmethod
    def envoyer(cls, user, titre, message, lien=""):
        """Méthode envoyer() définie dans le diagramme UML."""
        return cls.objects.create(user=user, titre=titre, message=message, lien=lien)
