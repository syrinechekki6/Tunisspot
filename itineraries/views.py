import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from spots.models import Lieu
from users.models import Notification
from .models import Itineraire, Etape, ListeFavoris, SortieGroupe, PropositionLieu, Vote
from .forms import ItineraireForm, EtapeForm, ListeFavorisForm, SortieGroupeForm

def itinerary_list(request):
    itineraires = Itineraire.objects.filter(est_public=True).order_by('-date_creation')
    return render(request, 'itineraries/itinerary_list.html', {'itineraires': itineraires})

def itinerary_detail(request, lien_partage):
    itineraire = get_object_or_404(Itineraire, lien_partage=lien_partage)
    etapes = itineraire.etapes.select_related('lieu').order_by('ordre')
    return render(request, 'itineraries/itinerary_detail.html', {
        'itineraire': itineraire,
        'etapes': etapes,
    })

def generator(request):
    """FONCTION UNIQUE : « Générateur de Journée Parfaite » (RF16)"""
    programme_genere = None
    duree_choisie = request.GET.get('duree', 'JOURNEE')
    budget_choisi = request.GET.get('budget', 'MOYEN')
    ambiance_choisie = request.GET.get('ambiance', 'ROMANTIQUE')

    if request.GET.get('generate') == '1':
        spots_pool = list(Lieu.objects.filter(statut='ACTIF'))
        
        if ambiance_choisie == 'ROMANTIQUE':
            candidats = [s for s in spots_pool if s.ambiance_romantique or s.vue_mer or s.quartier.nom in ['Sidi Bou Saïd', 'Gammarth', 'La Marsa']]
        elif ambiance_choisie == 'CULTURE':
            candidats = [s for s in spots_pool if s.categorie.slug in ['culture'] or s.quartier.nom in ['Médina de Tunis', 'Carthage']]
        elif ambiance_choisie == 'DETENTE':
            candidats = [s for s in spots_pool if s.vue_mer or s.terrasse or s.quartier.nom in ['La Marsa', 'Sidi Bou Saïd']]
        else:
            candidats = [s for s in spots_pool if s.categorie.slug in ['restaurants', 'cafes']]

        if len(candidats) < 3:
            candidats = spots_pool

        cafes = [s for s in candidats if s.categorie.slug == 'cafes'] or spots_pool
        restos = [s for s in candidats if s.categorie.slug == 'restaurants'] or spots_pool
        autres = [s for s in candidats if s.categorie.slug in ['culture', 'rooftops', 'activites']] or spots_pool

        etape1 = random.choice(cafes)
        etape2 = random.choice([s for s in outros if s != etape1] if (outros := [s for s in autres if s != etape1]) else restos)
        etape3 = random.choice([s for s in restos if s not in [etape1, etape2]] or spots_pool)

        programme_genere = [
            {'ordre': 1, 'moment': '10:00 - Pause Matinale', 'spot': etape1, 'action': 'Dégustation café/thé & douceurs', 'duree': '60 min', 'transport': 'Départ'},
            {'ordre': 2, 'moment': '12:30 - Découverte & Balade', 'spot': etape2, 'action': 'Visite culturelle ou flânerie panoramique', 'duree': '90 min', 'transport': 'TGM / 15 min'},
            {'ordre': 3, 'moment': '15:30 - Halte Gourmande', 'spot': etape3, 'action': 'Saveurs tunisiennes au bord de mer ou patio', 'duree': '120 min', 'transport': 'À pied / 10 min'},
        ]

        if duree_choisie == 'JOURNEE':
            rooftops = [s for s in spots_pool if s.categorie.slug == 'rooftops' or s.vue_mer] or spots_pool
            etape4 = random.choice([s for s in rooftops if s not in [etape1, etape2, etape3]] or spots_pool)
            programme_genere.append(
                {'ordre': 4, 'moment': '18:30 - Coucher de Soleil & Chill', 'spot': etape4, 'action': 'Vue magique sur le golfe de Tunis', 'duree': '90 min', 'transport': 'Taxi / 10 min'}
            )

    return render(request, 'itineraries/generator.html', {
        'programme_genere': programme_genere,
        'duree_choisie': duree_choisie,
        'budget_choisi': budget_choisi,
        'ambiance_choisie': ambiance_choisie,
    })

# CRUD ITINÉRAIRES (Ajouter, Modifier, Supprimer)
@login_required
def itinerary_create(request):
    if request.method == 'POST':
        form = ItineraireForm(request.POST)
        if form.is_valid():
            itin = form.save(commit=False)
            itin.user = request.user
            itin.save()

            request.user.points += 25
            request.user.save(update_fields=['points'])

            messages.success(request, f"Votre itinéraire '{itin.titre}' a été créé dans la base de données ! (+25 points)")
            return redirect('itineraries:itinerary_detail', lien_partage=itin.lien_partage)
    else:
        form = ItineraireForm()

    return render(request, 'itineraries/itinerary_form.html', {'form': form, 'title': 'Créer un itinéraire personnalisé'})

@login_required
def itinerary_edit(request, pk):
    itin = get_object_or_404(Itineraire, pk=pk)
    if itin.user != request.user and not (request.user.is_staff or request.user.role == 'ADMIN'):
        messages.error(request, "Permission refusée.")
        return redirect('itineraries:itinerary_list')

    if request.method == 'POST':
        form = ItineraireForm(request.POST, instance=itin)
        if form.is_valid():
            form.save()
            messages.success(request, f"L'itinéraire '{itin.titre}' a été modifié dans la base de données.")
            return redirect('itineraries:itinerary_detail', lien_partage=itin.lien_partage)
    else:
        form = ItineraireForm(instance=itin)

    return render(request, 'itineraries/itinerary_form.html', {'form': form, 'title': f"Modifier {itin.titre}"})

@login_required
def itinerary_delete(request, pk):
    itin = get_object_or_404(Itineraire, pk=pk)
    if itin.user != request.user and not (request.user.is_staff or request.user.role == 'ADMIN'):
        messages.error(request, "Permission refusée.")
        return redirect('itineraries:itinerary_list')

    if request.method == 'POST':
        titre = itin.titre
        itin.delete()
        messages.success(request, f"L'itinéraire '{titre}' a été supprimé de la base de données.")
        return redirect('itineraries:my_itineraries')

    return render(request, 'itineraries/itinerary_confirm_delete.html', {'itineraire': itin})

@login_required
def create_with_spot(request, spot_id):
    spot = get_object_or_404(Lieu, pk=spot_id)
    itin = Itineraire.objects.create(
        user=request.user,
        titre=f"Sortie à {spot.nom} et alentours",
        description=f"Itinéraire incluant {spot.nom} ({spot.quartier.nom}).",
        budget=spot.prix_moyen + 20,
        duree_totale=180
    )
    Etape.objects.create(
        itineraire=itin,
        lieu=spot,
        ordre=1,
        duree_visite=90,
        mode_transport='PIED',
        duree_trajet=0,
        distance=0.0
    )
    messages.success(request, f"'{spot.nom}' a été ajouté comme première étape de votre nouvel itinéraire !")
    return redirect('itineraries:itinerary_detail', lien_partage=itin.lien_partage)

@login_required
def etape_add(request, itineraire_id):
    itin = get_object_or_404(Itineraire, pk=itineraire_id, user=request.user)
    if request.method == 'POST':
        form = EtapeForm(request.POST)
        if form.is_valid():
            etape = form.save(commit=False)
            etape.itineraire = itin
            etape.save()
            messages.success(request, f"L'étape {etape.lieu.nom} a été ajoutée !")
            return redirect('itineraries:itinerary_detail', lien_partage=itin.lien_partage)
    else:
        form = EtapeForm()

    return render(request, 'itineraries/etape_form.html', {'form': form, 'itineraire': itin})

@login_required
def etape_delete(request, pk):
    etape = get_object_or_404(Etape, pk=pk)
    itin_lien = etape.itineraire.lien_partage
    if etape.itineraire.user != request.user and not (request.user.is_staff or request.user.role == 'ADMIN'):
        messages.error(request, "Permission refusée.")
        return redirect('itineraries:itinerary_detail', lien_partage=itin_lien)

    nom_lieu = etape.lieu.nom
    etape.delete()
    messages.success(request, f"L'étape '{nom_lieu}' a été supprimée de l'itinéraire.")
    return redirect('itineraries:itinerary_detail', lien_partage=itin_lien)

@login_required
def my_itineraries(request):
    itineraires = Itineraire.objects.filter(user=request.user).order_by('-date_creation')
    return render(request, 'itineraries/itinerary_list.html', {'itineraires': itineraires, 'is_my_list': True})

# FAVORIS (RF20)
@login_required
def favoris(request):
    listes = ListeFavoris.objects.filter(user=request.user).prefetch_related('lieux')
    if not listes.exists():
        default_list = ListeFavoris.objects.create(user=request.user, nom="Mes coups de cœur")
        listes = [default_list]

    return render(request, 'itineraries/favoris.html', {'listes': listes})

@login_required
def toggle_favorite(request, spot_id):
    spot = get_object_or_404(Lieu, pk=spot_id)
    liste, _ = ListeFavoris.objects.get_or_create(user=request.user, nom="Mes coups de cœur")
    if spot in liste.lieux.all():
        liste.lieux.remove(spot)
        messages.info(request, f"'{spot.nom}' retiré de vos favoris.")
    else:
        liste.lieux.add(spot)
        stat, _ = spot.statistiques.get_or_create(date_stat=timezone.now().date())
        stat.nombre_ajouts_favoris += 1
        stat.save(update_fields=['nombre_ajouts_favoris'])
        messages.success(request, f"'{spot.nom}' ajouté à vos favoris ❤️")

    return redirect(request.META.get('HTTP_REFERER', 'spots:home'))

# SORTIES DE GROUPE & VOTES (Module 5)
@login_required
def group_trips(request):
    sorties = SortieGroupe.objects.filter(createur=request.user).order_by('-date_sortie')
    if request.method == 'POST':
        form = SortieGroupeForm(request.POST)
        if form.is_valid():
            sg = form.save(commit=False)
            sg.createur = request.user
            sg.save()
            messages.success(request, f"Sortie de groupe '{sg.titre}' créée ! Partagez le code {sg.code_invitation} avec vos amis.")
            return redirect('itineraries:group_trip_detail', code=sg.code_invitation)
    else:
        form = SortieGroupeForm()

    return render(request, 'itineraries/group_trips.html', {'sorties': sorties, 'form': form})

@login_required
def group_trip_detail(request, code):
    sortie = get_object_or_404(SortieGroupe, code_invitation=code)
    propositions = sortie.propositions.select_related('lieu', 'propose_par').all()
    lieux_disponibles = Lieu.objects.filter(statut='ACTIF').order_by('nom')

    if request.method == 'POST' and 'propose_lieu' in request.POST:
        lieu_id = request.POST.get('lieu_id')
        comm = request.POST.get('commentaire', '')
        lieu = get_object_or_404(Lieu, pk=lieu_id)
        PropositionLieu.objects.create(sortie=sortie, lieu=lieu, propose_par=request.user, commentaire=comm)
        messages.success(request, f"'{lieu.nom}' proposé au vote !")
        return redirect('itineraries:group_trip_detail', code=code)

    return render(request, 'itineraries/group_trip_detail.html', {
        'sortie': sortie,
        'propositions': propositions,
        'lieux_disponibles': lieux_disponibles,
    })

@login_required
def vote_proposition(request, prop_id):
    prop = get_object_or_404(PropositionLieu, pk=prop_id)
    vote, created = Vote.objects.get_or_create(proposition=prop, user=request.user)
    if not created:
        vote.vote_pour = not vote.vote_pour
        vote.save()
    messages.success(request, f"Votre vote pour {prop.lieu.nom} a été enregistré dans la base de données !")
    return redirect('itineraries:group_trip_detail', code=prop.sortie.code_invitation)
