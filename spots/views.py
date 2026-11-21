import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Lieu, Categorie, Quartier, Revendication, Signalement
from .forms import LieuForm, RevendicationForm, SignalementForm
from .permissions import is_admin, is_etablissement_owner, can_manage_lieu_and_menu, admin_required


def home(request):
    top_spots = Lieu.objects.filter(statut='ACTIF').order_by('-note_moyenne')[:8]
    pepites = Lieu.objects.filter(statut='ACTIF', est_pepite_locale=True)[:3]
    if not pepites.exists():
        pepites = top_spots[:3]
    total_spots = Lieu.objects.filter(statut='ACTIF').count()
    return render(request, 'spots/home.html', {
        'top_spots': top_spots,
        'pepites': pepites,
        'total_spots': total_spots,
    })


def spot_list(request):
    if request.user.is_authenticated and is_admin(request.user):
        spots = Lieu.objects.all()
    else:
        spots = Lieu.objects.filter(statut='ACTIF')

    query = request.GET.get('q')
    if query:
        spots = spots.filter(
            Q(nom__icontains=query) |
            Q(description__icontains=query) |
            Q(adresse__icontains=query) |
            Q(quartier__nom__icontains=query) |
            Q(categorie__libelle__icontains=query)
        ).distinct()

    quartier_nom = request.GET.get('quartier')
    if quartier_nom:
        spots = spots.filter(quartier__nom=quartier_nom)

    cat_slug = request.GET.get('categorie')
    if cat_slug:
        spots = spots.filter(categorie__slug=cat_slug)

    prix = request.GET.get('prix')
    if prix:
        spots = spots.filter(fourchette_prix=prix)

    ambiances = {
        'wifi': request.GET.get('wifi'),
        'terrasse': request.GET.get('terrasse'),
        'parking': request.GET.get('parking'),
        'acces_pmr': request.GET.get('acces_pmr'),
        'vue_mer': request.GET.get('vue_mer'),
        'climatisation': request.GET.get('climatisation'),
        'ambiance_romantique': request.GET.get('romantique'),
        'ambiance_famille': request.GET.get('famille'),
        'ambiance_amis': request.GET.get('amis'),
        'halal': request.GET.get('halal'),
        'vegetarien': request.GET.get('vegetarien'),
    }
    for field, val in ambiances.items():
        if val == '1':
            spots = spots.filter(**{field: True})

    spots = spots.order_by('-note_moyenne')
    quartiers = Quartier.objects.all()
    categories = Categorie.objects.all()
    return render(request, 'spots/spot_list.html', {
        'spots': spots,
        'quartiers': quartiers,
        'categories': categories,
    })


def spot_detail(request, slug):
    spot = get_object_or_404(Lieu, slug=slug)
    return render(request, 'spots/spot_detail.html', {'spot': spot})


def random_spot(request):
    spots = list(Lieu.objects.filter(statut='ACTIF'))
    spot = random.choice(spots) if spots else None
    return render(request, 'spots/random_spot.html', {'spot': spot})


@login_required
def spot_create(request):
    if request.method == 'POST':
        form = LieuForm(request.POST)
        if form.is_valid():
            lieu = form.save(commit=False)
            lieu.proprietaire = request.user
            lieu.statut = 'EN_ATTENTE' if not is_admin(request.user) else 'ACTIF'
            lieu.save()
            messages.success(request, f"Lieu '{lieu.nom}' cree avec succes !")
            return redirect('spots:spot_detail', slug=lieu.slug)
    else:
        form = LieuForm()
    return render(request, 'spots/spot_form.html', {'form': form, 'action': 'Creer'})


@login_required
def spot_edit(request, pk):
    lieu = get_object_or_404(Lieu, pk=pk)
    if not (is_admin(request.user) or lieu.proprietaire == request.user):
        messages.error(request, "Acces refuse.")
        return redirect('spots:spot_detail', slug=lieu.slug)
    if request.method == 'POST':
        form = LieuForm(request.POST, instance=lieu)
        if form.is_valid():
            form.save()
            messages.success(request, f"Lieu '{lieu.nom}' modifie.")
            return redirect('spots:spot_detail', slug=lieu.slug)
    else:
        form = LieuForm(instance=lieu)
    return render(request, 'spots/spot_form.html', {'form': form, 'lieu': lieu, 'action': 'Modifier'})


@login_required
def spot_delete(request, pk):
    lieu = get_object_or_404(Lieu, pk=pk)
    if not is_admin(request.user):
        messages.error(request, "Acces refuse.")
        return redirect('spots:spot_detail', slug=lieu.slug)
    if request.method == 'POST':
        nom = lieu.nom
        lieu.delete()
        messages.success(request, f"Lieu '{nom}' supprime.")
        return redirect('spots:spot_list')
    return render(request, 'spots/spot_confirm_delete.html', {'lieu': lieu})


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
            messages.success(request, "Votre revendication a ete soumise.")
            return redirect('spots:spot_detail', slug=lieu.slug)
    else:
        form = RevendicationForm()
    return render(request, 'spots/claim_form.html', {'form': form, 'lieu': lieu})


@login_required
def signalement_create(request, lieu_id):
    lieu = get_object_or_404(Lieu, pk=lieu_id)
    if request.method == 'POST':
        form = SignalementForm(request.POST)
        if form.is_valid():
            sig = form.save(commit=False)
            sig.lieu = lieu
            sig.user = request.user
            sig.save()
            messages.success(request, "Signalement envoye. Merci !")
            return redirect('spots:spot_detail', slug=lieu.slug)
    else:
        form = SignalementForm()
    return render(request, 'spots/signalement_form.html', {'form': form, 'lieu': lieu})
