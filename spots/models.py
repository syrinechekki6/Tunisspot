from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from users.models import Utilisateur

class Categorie(models.Model):
    libelle = models.CharField(max_length=100, unique=True)
    libelle_ar = models.CharField(max_length=100, blank=True, null=True)
    libelle_en = models.CharField(max_length=100, blank=True, null=True)
    icone = models.CharField(max_length=50, default='fa-utensils', help_text="Ex: fa-utensils, fa-coffee, fa-landmark")
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
        ('€', 'Économique (< 15 DT)'),
        ('€€', 'Moyen (15 - 40 DT)'),
        ('€€€', 'Haut de gamme (> 40 DT)'),
    )
    STATUT_CHOICES = (
        ('ACTIF', 'Actif'),
        ('EN_ATTENTE', 'En attente de validation'),
        ('FERME', 'Fermé temporairement'),
    )
    FOULE_CHOICES = (
        ('Faible', 'Calme (peu de monde)'),
        ('Moyen', 'Affluence modérée'),
        ('Élevé', 'Très fréquenté'),
    )

    place_id = models.CharField(max_length=150, blank=True, null=True, unique=True, verbose_name="Google Place ID")
    nom = models.CharField(max_length=200, verbose_name="Nom de l'établissement")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='lieux')
    quartier = models.ForeignKey(Quartier, on_delete=models.SET_NULL, null=True, blank=True, related_name='lieux')
    adresse = models.CharField(max_length=300)
    latitude = models.FloatField(default=36.8065)
    longitude = models.FloatField(default=10.1815)
    
    telephone = models.CharField(max_length=50, blank=True, null=True)
    site_web = models.URLField(max_length=300, blank=True, null=True)
    fourchette_prix = models.CharField(max_length=5, choices=PRIX_CHOICES, default='€€')
    prix_moyen = models.FloatField(default=25.0, help_text="Prix moyen indicatif par personne en Dinars Tunisiens")
    horaires = models.CharField(max_length=255, default='Tous les jours de 08:00 à 23:00')
    description = models.TextField(blank=True, null=True)
    
    # Images
    image_principale = models.CharField(max_length=500, default='https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80')
    
    # Indicateurs uniques & algorithme
    note_moyenne = models.FloatField(default=4.5)
    nombre_avis = models.IntegerField(default=0)
    est_pepite_locale = models.BooleanField(default=False, verbose_name="Label Pépite Locale")
    indice_foule = models.CharField(max_length=20, choices=FOULE_CHOICES, default='Moyen')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF')
    
    # Équipements & Ambiances (Filtres RF05)
    wifi = models.BooleanField(default=True, verbose_name="Wi-Fi gratuit")
    terrasse = models.BooleanField(default=True, verbose_name="Terrasse extérieure")
    parking = models.BooleanField(default=False, verbose_name="Parking disponible")
    acces_pmr = models.BooleanField(default=True, verbose_name="Accès PMR / handicapés")
    vue_mer = models.BooleanField(default=False, verbose_name="Vue sur mer")
    climatisation = models.BooleanField(default=True, verbose_name="Climatisation")
    ambiance_romantique = models.BooleanField(default=False, verbose_name="Idéal en couple / Romantique")
    ambiance_famille = models.BooleanField(default=True, verbose_name="Adapté aux familles")
    ambiance_amis = models.BooleanField(default=True, verbose_name="Sortie entre amis")
    halal = models.BooleanField(default=True, verbose_name="100% Halal")
    vegetarien = models.BooleanField(default=False, verbose_name="Options végétariennes")

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

    def calculer_note_moyenne(self):
        avis_approuves = self.avis.filter(statut_moderation='APPROUVE')
        if avis_approuves.exists():
            # Pondération par score de confiance
            total_points = sum(a.note * a.score_confiance for a in avis_approuves)
            total_weights = sum(a.score_confiance for a in avis_approuves)
            self.note_moyenne = round(total_points / total_weights, 1) if total_weights > 0 else 4.0
            self.nombre_avis = avis_approuves.count()
            
            # Calcul automatique du "Label Pépite locale"
            # Plus de 70% d'avis de résidents avec note >= 4.2
            residents_avis = avis_approuves.filter(type_visiteur='RESIDENT')
            if avis_approuves.count() >= 2 and residents_avis.count() / avis_approuves.count() >= 0.6 and self.note_moyenne >= 4.3:
                self.est_pepite_locale = True
            self.save(update_fields=['note_moyenne', 'nombre_avis', 'est_pepite_locale'])
        return self.note_moyenne

    @property
    def est_ouvert(self):
        return True # Simplification intelligente temps réel

class Plat(models.Model):
    CATEGORIE_PLAT_CHOICES = (
        ('Entrée', 'Entrée / Salade'),
        ('Plat principal', 'Plat principal'),
        ('Dessert', 'Dessert & Pâtisserie'),
        ('Boisson', 'Boisson & Café'),
        ('Spécialité Tunisienne', 'Spécialité Tunisienne'),
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

class Avis(models.Model):
    STATUT_MODERATION_CHOICES = (
        ('APPROUVE', 'Approuvé'),
        ('EN_ATTENTE', 'En attente'),
        ('REJETE', 'Rejeté'),
    )
    TYPE_VISITEUR_CHOICES = (
        ('RESIDENT', 'Résident tunisien'),
        ('TOURISTE', 'Touriste de passage'),
    )

    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, related_name='avis')
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='avis')
    note = models.IntegerField(default=5, help_text="Note globale de 1 à 5")
    
    # Notes par critères (RF10)
    note_qualite = models.IntegerField(default=5)
    note_service = models.IntegerField(default=5)
    note_prix = models.IntegerField(default=5)
    note_ambiance = models.IntegerField(default=5)
    
    commentaire = models.TextField()
    date_publication = models.DateTimeField(default=timezone.now)
    statut_moderation = models.CharField(max_length=20, choices=STATUT_MODERATION_CHOICES, default='APPROUVE')
    nombre_signalements = models.IntegerField(default=0)
    score_confiance = models.FloatField(default=1.0, help_text="Score de confiance (0.1 à 1.0) calculé selon l'ancienneté")
    type_visiteur = models.CharField(max_length=20, choices=TYPE_VISITEUR_CHOICES, default='RESIDENT')

    class Meta:
        ordering = ['-date_publication']

    def __str__(self):
        return f"Avis {self.note}/5 par {self.user.username} sur {self.lieu.nom}"

    def save(self, *args, **kwargs):
        # Calcul du score de confiance de l'avis
        score = 0.5
        if self.user.date_inscription and (timezone.now() - self.user.date_inscription).days > 30:
            score += 0.2
        if len(self.commentaire) > 50:
            score += 0.2
        if self.user.est_guide_local:
            score += 0.1
        self.score_confiance = min(1.0, round(score, 2))
        
        # Attribution du type de visiteur selon le rôle du compte
        if self.user.role == 'RESIDENT':
            self.type_visiteur = 'RESIDENT'
        elif self.user.role == 'TOURISTE':
            self.type_visiteur = 'TOURISTE'
            
        super().save(*args, **kwargs)
        self.lieu.calculer_note_moyenne()

    def soumettre(self):
        """Méthode soumettre() définie dans le diagramme UML."""
        self.statut_moderation = 'EN_ATTENTE'
        self.save()

    def approuver(self):
        """Méthode approuver() définie dans le diagramme UML."""
        self.statut_moderation = 'APPROUVE'
        self.save(update_fields=['statut_moderation'])
        self.lieu.calculer_note_moyenne()

    def rejeter(self):
        """Méthode rejeter() définie dans le diagramme UML."""
        self.statut_moderation = 'REJETE'
        self.save(update_fields=['statut_moderation'])
        self.lieu.calculer_note_moyenne()

class Photo(models.Model):
    STATUT_MODERATION_CHOICES = (
        ('APPROUVE', 'Approuvé'),
        ('EN_ATTENTE', 'En attente'),
        ('REJETE', 'Rejeté'),
    )
    SOURCE_CHOICES = (
        ('COMMUNAUTE', 'Communauté'),
        ('PROPRIETAIRE', 'Propriétaire'),
        ('GOOGLE', 'Google Places'),
    )

    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, related_name='photos')
    user = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='photos')
    url = models.CharField(max_length=500)
    legende = models.CharField(max_length=200, blank=True, null=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='COMMUNAUTE')
    statut_moderation = models.CharField(max_length=20, choices=STATUT_MODERATION_CHOICES, default='APPROUVE')
    date_ajout = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Photo {self.id} de {self.lieu.nom}"

    def approuver(self):
        """Méthode approuver() définie dans le diagramme UML."""
        self.statut_moderation = 'APPROUVE'
        self.save(update_fields=['statut_moderation'])

    def rejeter(self):
        """Méthode rejeter() définie dans le diagramme UML."""
        self.statut_moderation = 'REJETE'
        self.save(update_fields=['statut_moderation'])

class Revendication(models.Model):
    STATUT_CHOICES = (
        ('EN_ATTENTE', 'En attente'),
        ('APPROUVEE', 'Approuvée'),
        ('REJETEE', 'Rejetée'),
    )
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, related_name='revendications')
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='revendications')
    justificatif = models.TextField(help_text="Expliquez votre lien avec l'établissement (ex: Gérant, Registre de commerce)")
    telephone_contact = models.CharField(max_length=30)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    date_demande = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Revendication de {self.user.username} pour {self.lieu.nom}"

class Signalement(models.Model):
    STATUT_CHOICES = (
        ('NOUVEAU', 'Nouveau'),
        ('EN_COURS', 'En cours d\'examen'),
        ('RESOLU', 'Résolu'),
        ('REJETE', 'Rejeté'),
    )
    MOTIF_CHOICES = (
        ('FERME', 'Établissement fermé définitivement'),
        ('INFO_FAUSSE', 'Informations ou horaires incorrects'),
        ('SPAM_AVIS', 'Avis faux ou abusif'),
        ('PHOTO_INAPPROPRIEE', 'Photo inappropriée'),
        ('AUTRE', 'Autre signalement'),
    )

    user = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='signalements')
    lieu = models.ForeignKey(Lieu, on_delete=models.CASCADE, null=True, blank=True, related_name='signalements')
    avis = models.ForeignKey(Avis, on_delete=models.CASCADE, null=True, blank=True, related_name='signalements')
    motif = models.CharField(max_length=30, choices=MOTIF_CHOICES)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='NOUVEAU')
    date_signalement = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Signalement #{self.id} ({self.get_motif_display()})"
