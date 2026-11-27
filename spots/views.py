import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.utils import timezone
from .models import Lieu, Categorie, Quartier, Plat, Avis, Photo, Revendication, Signalement
from .forms import LieuForm, PlatForm, AvisForm, PhotoForm, RevendicationForm, SignalementForm
from events.models import Evenement, OffrePromotion
from itineraries.models import ListeFavoris
from users.models import Utilisateur, Notification
from .permissions import is_admin, is_etablissement_owner, can_manage_lieu_and_menu, admin_required

def home(request):
    top_spots = Lieu.objects.filter(statut='ACTIF').order_by('-note_moyenne')[:8]
    pepites = Lieu.objects.filter(statut='ACTIF', est_pepite_locale=True)[:3]
    if not pepites.exists():
        pepites = top_spots[:3]
    
    events = Evenement.objects.filter(date_fin__gte=timezone.now()).order_by('date_debut')[:4]
    total_spots = Lieu.objects.filter(statut='ACTIF').count()

    return render(request, 'spots/home.html', {
        'top_spots': top_spots,
        'pepites': pepites,
        'events': events,
        'total_spots': total_spots,
    })

def spot_list(request):
    # Pour l'admin : visibilité complète des lieux (y compris EN_ATTENTE pour modération)
    if request.user.is_authenticated and is_admin(request.user):
        spots = Lieu.objects.all()
    else:
        spots = Lieu.objects.filter(statut='ACTIF')
    
    # Query Search (Multi-critères : nom, description, adresse, quartier, catégorie, plats du menu)
    query = request.GET.get('q')
    if query:
        spots = spots.filter(
            Q(nom__icontains=query) | 
            Q(description__icontains=query) | 
            Q(adresse__icontains=query) |
            Q(quartier__nom__icontains=query) |
            Q(categorie__libelle__icontains=query) |
            Q(plats__nom__icontains=query)
        ).distinct()

    # Quartier filter
    quartier_nom = request.GET.get('quartier')
    if quartier_nom:
        spots = spots.filter(quartier__nom__iexact=quartier_nom)

    # Categorie filter
    categorie_slug = request.GET.get('categorie')
    if categorie_slug:
        spots = spots.filter(categorie__slug=categorie_slug)

    # Prix filter
    prix = request.GET.get('prix')
    if prix:
        spots = spots.filter(fourchette_prix=prix)

    # Note Min filter
    note_min = request.GET.get('note_min')
    if note_min:
        try:
            spots = spots.filter(note_moyenne__gte=float(note_min))
        except ValueError:
            pass

    # Pepite Locale filter
    pepite = request.GET.get('pepite')
    if pepite == '1':
        spots = spots.filter(est_pepite_locale=True)

    # Amenities
    if request.GET.get('terrasse') == '1':
        spots = spots.filter(terrasse=True)
    if request.GET.get('vue_mer') == '1':
        spots = spots.filter(vue_mer=True)
    if request.GET.get('wifi') == '1':
        spots = spots.filter(wifi=True)
    if request.GET.get('romantique') == '1':
        spots = spots.filter(ambiance_romantique=True)
    if request.GET.get('vegetarien') == '1':
        spots = spots.filter(vegetarien=True)
    if request.GET.get('acces_pmr') == '1':
        spots = spots.filter(acces_pmr=True)

    # Tri / Sorting (RF06)
    tri = request.GET.get('tri', 'note')
    if tri == 'note':
        spots = spots.order_by('-note_moyenne', '-nombre_avis')
    elif tri == 'populaire':
        spots = spots.order_by('-nombre_avis', '-note_moyenne')
    elif tri == 'prix_asc':
        spots = spots.order_by('prix_moyen')
    elif tri == 'prix_desc':
        spots = spots.order_by('-prix_moyen')
    elif tri == 'recent':
        spots = spots.order_by('-date_creation')

    # Événements et Offres pour exploration unifiée
    type_filtre = request.GET.get('type', 'lieux')
    events = Evenement.objects.all().select_related('lieu', 'cree_par').order_by('-date_debut')
    offres = OffrePromotion.objects.all().select_related('lieu', 'cree_par').order_by('-reduction_pourcentage')

    if query:
        events = events.filter(Q(titre__icontains=query) | Q(description__icontains=query) | Q(lieu__nom__icontains=query))
        offres = offres.filter(Q(titre__icontains=query) | Q(description__icontains=query) | Q(lieu__nom__icontains=query) | Q(code_promo__icontains=query))

    total_results = spots.count()
    return render(request, 'spots/spot_list.html', {
        'spots': spots,
        'events': events,
        'offres': offres,
        'total_results': total_results,
        'total_events': events.count(),
        'total_offres': offres.count(),
        'type_filtre': type_filtre,
        'query': query,
        'selected_quartier': quartier_nom,
        'selected_categorie': categorie_slug,
        'selected_prix': prix,
        'selected_note_min': note_min,
        'selected_tri': tri,
        'selected_pepite': pepite == '1',
        'selected_terrasse': request.GET.get('terrasse') == '1',
        'selected_vue_mer': request.GET.get('vue_mer') == '1',
        'selected_wifi': request.GET.get('wifi') == '1',
        'selected_romantique': request.GET.get('romantique') == '1',
        'selected_vegetarien': request.GET.get('vegetarien') == '1',
        'selected_acces_pmr': request.GET.get('acces_pmr') == '1',
    })

def spot_detail(request, slug):
    from django.http import Http404
    spot = get_object_or_404(Lieu, slug=slug)
    
    # Workflow de validation : un lieu EN_ATTENTE n'est visible que par son auteur et l'Admin
    if spot.statut == 'EN_ATTENTE':
        if not (request.user.is_authenticated and (is_admin(request.user) or spot.proprietaire_id == request.user.id)):
            raise Http404("Ce lieu est en attente de validation par l'administration.")

    # Increment view counter
    stat, _ = spot.statistiques.get_or_create(date_stat=timezone.now().date())
    stat.nombre_vues += 1
    stat.save(update_fields=['nombre_vues'])

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = ListeFavoris.objects.filter(user=request.user, lieux=spot).exists()

    return render(request, 'spots/spot_detail.html', {
        'spot': spot,
        'is_favorite': is_favorite,
    })

def random_spot(request):
    """Fonctionnalité signature de Win Tokhrej : 'Laisse le hasard choisir ta sortie !'"""
    spots = Lieu.objects.filter(statut='ACTIF')
    quartier_id = request.GET.get('quartier')
    if quartier_id:
        spots = spots.filter(quartier__nom=quartier_id)

    count = spots.count()
    spot = None
    if count > 0:
        random_index = random.randint(0, count - 1)
        spot = spots[random_index]

    return render(request, 'spots/random_spot.html', {
        'spot': spot,
        'selected_quartier': quartier_id,
    })

@login_required
def spot_create(request):
    if request.method == 'POST':
        form = LieuForm(request.POST)
        if form.is_valid():
            lieu = form.save(commit=False)
            lieu.proprietaire = request.user
            
            # Workflow de validation :
            # - Admin -> Publication immédiate (ACTIF)
            # - Visiteur / Établissement -> Soumis pour validation (EN_ATTENTE)
            if is_admin(request.user):
                lieu.statut = 'ACTIF'
                lieu.save()
                messages.success(request, f"Le spot '{lieu.nom}' a été publié immédiatement en tant qu'administrateur.")
            else:
                lieu.statut = 'EN_ATTENTE'
                lieu.save()
                
                # Notification envoyée aux administrateurs
                admins = Utilisateur.objects.filter(Q(is_staff=True) | Q(role='ADMIN')).distinct()
                for adm in admins:
                    Notification.objects.create(
                        user=adm,
                        titre=f"Nouveau lieu en attente : {lieu.nom}",
                        message=f"{request.user.username} a soumis '{lieu.nom}' pour validation.",
                        lien=f"/spot/{lieu.slug}/"
                    )

                messages.info(request, f"Votre lieu '{lieu.nom}' a été soumis avec succès ! Il est en attente de validation par l'administrateur.")

            return redirect('spots:spot_detail', slug=lieu.slug)
    else:
        form = LieuForm()

    return render(request, 'spots/spot_form.html', {'form': form, 'title': 'Proposer une nouvelle adresse à Tunis'})

@login_required
def spot_edit(request, pk):
    lieu = get_object_or_404(Lieu, pk=pk)
    if not (request.user.is_staff or request.user.role == 'ADMIN' or lieu.proprietaire == request.user):
        messages.error(request, "Vous n'avez pas la permission de modifier ce lieu.")
        return redirect('spots:spot_detail', slug=lieu.slug)

    if request.method == 'POST':
        form = LieuForm(request.POST, instance=lieu)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le spot '{lieu.nom}' a été mis à jour.")
            return redirect('spots:spot_detail', slug=lieu.slug)
    else:
        form = LieuForm(instance=lieu)

    return render(request, 'spots/spot_form.html', {'form': form, 'title': f"Modifier {lieu.nom}", 'lieu': lieu})

@login_required
def spot_delete(request, pk):
    lieu = get_object_or_404(Lieu, pk=pk)
    if not (request.user.is_staff or request.user.role == 'ADMIN' or lieu.proprietaire == request.user):
        messages.error(request, "Permission refusée.")
        return redirect('spots:spot_detail', slug=lieu.slug)

    if request.method == 'POST':
        nom = lieu.nom
        lieu.delete()
        messages.success(request, f"Le spot '{nom}' a été supprimé.")
        return redirect('spots:spot_list')

    return render(request, 'spots/spot_confirm_delete.html', {'lieu': lieu})

# Fonctions utilitaires de contrôle des permissions
def can_manage_lieu_menu(user, lieu):
    """
    Règle stricte :
    - Un Admin gère tout.
    - Un compte Établissement gère UNIQUEMENT le menu de son propre lieu assigné.
    - Aucun autre compte ne peut modifier un menu tiers ou non assigné.
    """
    return can_manage_lieu_and_menu(user, lieu)

def can_manage_avis(user, avis):
    if not user.is_authenticated:
        return False
    if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
        return True
    return avis.user == user

def can_manage_photo(user, photo):
    if not user.is_authenticated:
        return False
    if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
        return True
    if photo.user == user:
        return True
    if photo.lieu and photo.lieu.proprietaire == user:
        return True
    return False

# VUE DÉDIÉE AU MENU NUMÉRIQUE DU SPOT
def spot_menu_detail(request, slug):
    """Accès direct et clair au menu d'un établissement précis (RF08)"""
    spot = get_object_or_404(Lieu, slug=slug)
    categories = ['Spécialité Tunisienne', 'Entrée', 'Plat principal', 'Dessert', 'Boisson']
    menu_par_cat = {}
    for cat in categories:
        plats = spot.plats.filter(categorie_plat=cat)
        if plats.exists():
            menu_par_cat[cat] = plats
    autres = spot.plats.exclude(categorie_plat__in=categories)
    if autres.exists():
        menu_par_cat['Autres délices'] = autres

    can_manage = can_manage_lieu_menu(request.user, spot)

    # Incrémenter les stats de vue du menu
    stat, _ = spot.statistiques.get_or_create(date_stat=timezone.now().date())
    stat.nombre_clics_menu += 1
    stat.save(update_fields=['nombre_clics_menu'])

    return render(request, 'spots/spot_menu.html', {
        'spot': spot,
        'menu_par_cat': menu_par_cat,
        'can_manage': can_manage,
    })

# CRUD PLATS / MENUS NUMÉRIQUES
@login_required
def plat_create(request, lieu_id):
    lieu = get_object_or_404(Lieu, pk=lieu_id)
    if not can_manage_lieu_menu(request.user, lieu):
        messages.error(request, "Seul le propriétaire de cet établissement ou l'administrateur peut modifier le menu.")
        return redirect('spots:spot_detail', slug=lieu.slug)

    if request.method == 'POST':
        form = PlatForm(request.POST)
        if form.is_valid():
            plat = form.save(commit=False)
            plat.lieu = lieu
            plat.save()
            messages.success(request, f"Le plat '{plat.nom}' a été ajouté au menu de {lieu.nom}.")
            return redirect('spots:spot_detail', slug=lieu.slug)
    else:
        form = PlatForm()

    return render(request, 'spots/plat_form.html', {'form': form, 'lieu': lieu, 'title': f"Ajouter un plat au menu de {lieu.nom}"})

@login_required
def plat_edit(request, pk):
    plat = get_object_or_404(Plat, pk=pk)
    if not can_manage_lieu_menu(request.user, plat.lieu):
        messages.error(request, "Permission refusée : vous ne pouvez pas modifier ce plat.")
        return redirect('spots:spot_detail', slug=plat.lieu.slug)

    if request.method == 'POST':
        form = PlatForm(request.POST, instance=plat)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le plat '{plat.nom}' a été mis à jour avec succès.")
            return redirect('spots:spot_detail', slug=plat.lieu.slug)
    else:
        form = PlatForm(instance=plat)

    return render(request, 'spots/plat_form.html', {'form': form, 'lieu': plat.lieu, 'title': f"Modifier {plat.nom}"})

@login_required
def plat_delete(request, pk):
    plat = get_object_or_404(Plat, pk=pk)
    if not can_manage_lieu_menu(request.user, plat.lieu):
        messages.error(request, "Permission refusée : vous ne pouvez pas supprimer ce plat.")
        return redirect('spots:spot_detail', slug=plat.lieu.slug)

    lieu_slug = plat.lieu.slug
    if request.method == 'POST':
        nom = plat.nom
        plat.delete()
        messages.success(request, f"Le plat '{nom}' a été supprimé du menu.")
        return redirect('spots:spot_detail', slug=lieu_slug)

    return render(request, 'spots/plat_confirm_delete.html', {'plat': plat})

# CRUD AVIS (AVEC MODIFICATION ET SUPPRESSION)
@login_required
def avis_create(request, lieu_id):
    lieu = get_object_or_404(Lieu, pk=lieu_id)
    if request.method == 'POST':
        form = AvisForm(request.POST)
        if form.is_valid():
            avis = form.save(commit=False)
            avis.lieu = lieu
            avis.user = request.user
            avis.save()

            # Bonus points découverte
            request.user.points += 15
            request.user.save(update_fields=['points'])

            Notification.objects.create(
                user=request.user,
                titre="Avis publié !",
                message=f"Merci pour votre évaluation de {lieu.nom}. Vous remportez +15 points !",
                lien=f"/spot/{lieu.slug}/"
            )

            messages.success(request, "Votre avis a été publié avec succès ! (+15 points)")
            return redirect('spots:spot_detail', slug=lieu.slug)
    else:
        form = AvisForm()

    return render(request, 'spots/avis_form.html', {'form': form, 'lieu': lieu, 'title': f"Noter {lieu.nom}"})

@login_required
def avis_edit(request, pk):
    avis = get_object_or_404(Avis, pk=pk)
    if not can_manage_avis(request.user, avis):
        messages.error(request, "Vous ne pouvez modifier que vos propres avis.")
        return redirect('spots:spot_detail', slug=avis.lieu.slug)

    if request.method == 'POST':
        form = AvisForm(request.POST, instance=avis)
        if form.is_valid():
            avis = form.save()
            messages.success(request, "Votre avis a été mis à jour avec succès.")
            return redirect('spots:spot_detail', slug=avis.lieu.slug)
    else:
        form = AvisForm(instance=avis)

    return render(request, 'spots/avis_form.html', {'form': form, 'lieu': avis.lieu, 'title': f"Modifier mon avis sur {avis.lieu.nom}", 'is_edit': True})

@login_required
def avis_delete(request, pk):
    avis = get_object_or_404(Avis, pk=pk)
    if not can_manage_avis(request.user, avis):
        messages.error(request, "Vous ne pouvez supprimer que vos propres avis.")
        return redirect('spots:spot_detail', slug=avis.lieu.slug)

    lieu = avis.lieu
    if request.method == 'POST':
        avis.delete()
        lieu.calculer_note_moyenne()
        messages.success(request, "Votre avis a été supprimé.")
        return redirect('spots:spot_detail', slug=lieu.slug)

    return render(request, 'spots/avis_confirm_delete.html', {'avis': avis})

# CRUD PHOTOS DE LA COMMUNAUTÉ ET DU PROPRIÉTAIRE
@login_required
def photo_create(request, lieu_id):
    lieu = get_object_or_404(Lieu, pk=lieu_id)
    if request.method == 'POST':
        form = PhotoForm(request.POST)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.lieu = lieu
            photo.user = request.user
            if lieu.proprietaire == request.user:
                photo.source = 'PROPRIETAIRE'
            else:
                photo.source = 'COMMUNAUTE'
            photo.save()

            request.user.points += 10
            request.user.save(update_fields=['points'])

            messages.success(request, f"Votre photo pour {lieu.nom} a été ajoutée avec succès ! (+10 points)")
            return redirect('spots:spot_detail', slug=lieu.slug)
    else:
        form = PhotoForm()

    return render(request, 'spots/photo_form.html', {'form': form, 'lieu': lieu, 'title': f"Ajouter une photo de {lieu.nom}"})

@login_required
def photo_edit(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    if not can_manage_photo(request.user, photo):
        messages.error(request, "Vous n'avez pas la permission de modifier cette photo.")
        return redirect('spots:spot_detail', slug=photo.lieu.slug)

    if request.method == 'POST':
        form = PhotoForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, "La légende de la photo a été mise à jour.")
            return redirect('spots:spot_detail', slug=photo.lieu.slug)
    else:
        form = PhotoForm(instance=photo)

    return render(request, 'spots/photo_form.html', {'form': form, 'lieu': photo.lieu, 'title': f"Modifier la photo de {photo.lieu.nom}", 'is_edit': True})

@login_required
def photo_delete(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    if not can_manage_photo(request.user, photo):
        messages.error(request, "Vous n'avez pas la permission de supprimer cette photo.")
        return redirect('spots:spot_detail', slug=photo.lieu.slug)

    lieu_slug = photo.lieu.slug
    if request.method == 'POST':
        photo.delete()
        messages.success(request, "La photo a été supprimée.")
        return redirect('spots:spot_detail', slug=lieu_slug)

    return render(request, 'spots/photo_confirm_delete.html', {'photo': photo})

# REVENDICATION DE FICHE PROPRIÉTAIRE (RF30)
@login_required
def claim_spot(request, lieu_id):
    lieu = get_object_or_404(Lieu, pk=lieu_id)
    if request.method == 'POST':
        form = RevendicationForm(request.POST)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.lieu = lieu
            rev.user = request.user
            rev.save()
            messages.success(request, "Votre demande de revendication a été envoyée aux modérateurs. Vous serez notifié après vérification.")
            return redirect('spots:spot_detail', slug=lieu.slug)
    else:
        form = RevendicationForm()

    return render(request, 'spots/claim_form.html', {'form': form, 'lieu': lieu})

# SIGNALEMENT D'UN SPOT OU CONTENU (RF22)
def signalement_create(request, lieu_id):
    lieu = get_object_or_404(Lieu, pk=lieu_id)
    if request.method == 'POST':
        form = SignalementForm(request.POST)
        if form.is_valid():
            sig = form.save(commit=False)
            sig.lieu = lieu
            if request.user.is_authenticated:
                sig.user = request.user
            sig.save()
            messages.success(request, "Merci pour votre signalement. Notre équipe de modération va vérifier l'information.")
            return redirect('spots:spot_detail', slug=lieu.slug)
    else:
        form = SignalementForm()

    return render(request, 'spots/signalement_form.html', {'form': form, 'lieu': lieu})
