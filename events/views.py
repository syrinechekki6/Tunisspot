from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Evenement, OffrePromotion
from .forms import EvenementForm, OffrePromotionForm

def user_can_manage_event(user, ev):
    if not user.is_authenticated:
        return False
    if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
        return True
    return ev.cree_par_id == user.id

def user_can_manage_offre(user, off):
    if not user.is_authenticated:
        return False
    if user.is_staff or getattr(user, 'role', '') == 'ADMIN':
        return True
    return off.cree_par_id == user.id

def event_list(request):
    now = timezone.now()
    filtre = request.GET.get('filtre', 'tous')
    cat = request.GET.get('categorie')

    events_qs = Evenement.objects.all().select_related('lieu', 'cree_par')

    if filtre == 'a_venir':
        events_qs = events_qs.filter(date_fin__gte=now)
    elif filtre == 'mes_evenements' and request.user.is_authenticated:
        events_qs = events_qs.filter(cree_par=request.user)

    if cat:
        events_qs = events_qs.filter(categorie=cat)

    # Tri : à venir en priorité, puis par date récente
    events = events_qs.order_by('-est_populaire', '-date_debut')
    
    # Affichage des offres : actives non expirées, ou créées par l'utilisateur connecté
    if request.user.is_authenticated:
        offres = OffrePromotion.objects.filter(
            Q(est_active=True) |
            Q(cree_par=request.user)
        ).distinct().order_by('-reduction_pourcentage')
    else:
        offres = OffrePromotion.objects.filter(est_active=True).order_by('-reduction_pourcentage')

    return render(request, 'events/event_list.html', {
        'events': events,
        'offres': offres,
        'selected_cat': cat,
        'filtre': filtre,
        'now': now,
    })

# CRUD ÉVÉNEMENTS (Ajouter, Modifier, Supprimer)
@login_required
def event_create(request):
    if request.method == 'POST':
        form = EvenementForm(request.POST)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.cree_par = request.user
            ev.save()
            messages.success(request, f"L'événement '{ev.titre}' a été enregistré dans la base de données !")
            return redirect('events:event_list')
    else:
        form = EvenementForm()

    return render(request, 'events/event_form.html', {'form': form, 'title': 'Créer un événement culturel ou festif'})

@login_required
def event_edit(request, pk):
    ev = get_object_or_404(Evenement, pk=pk)
    if not user_can_manage_event(request.user, ev):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier cet événement.")
        return redirect('events:event_list')

    if request.method == 'POST':
        form = EvenementForm(request.POST, instance=ev)
        if form.is_valid():
            saved_ev = form.save(commit=False)
            if not saved_ev.cree_par:
                saved_ev.cree_par = request.user
            saved_ev.save()
            messages.success(request, f"L'événement '{saved_ev.titre}' a été modifié dans la base de données.")
            return redirect('events:event_list')
    else:
        form = EvenementForm(instance=ev)

    return render(request, 'events/event_form.html', {'form': form, 'title': f"Modifier {ev.titre}"})

@login_required
def event_delete(request, pk):
    ev = get_object_or_404(Evenement, pk=pk)
    if not user_can_manage_event(request.user, ev):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer cet événement.")
        return redirect('events:event_list')

    if request.method == 'POST':
        titre = ev.titre
        ev.delete()
        messages.success(request, f"L'événement '{titre}' a été supprimé de la base de données.")
        return redirect('events:event_list')

    return render(request, 'events/event_confirm_delete.html', {'event': ev})

# CRUD OFFRES PROMOTIONNELLES (Ajouter, Modifier, Supprimer)
@login_required
def offre_create(request):
    if request.method == 'POST':
        form = OffrePromotionForm(request.POST)
        if form.is_valid():
            off = form.save(commit=False)
            off.cree_par = request.user
            # S'assurer que l'offre est active si non décochée
            if 'est_active' not in request.POST and off.est_active is None:
                off.est_active = True
            off.save()
            messages.success(request, f"L'offre '{off.titre}' a été enregistrée dans la base de données !")
            return redirect('events:event_list')
    else:
        form = OffrePromotionForm(initial={'est_active': True})

    return render(request, 'events/offre_form.html', {'form': form, 'title': 'Créer une offre promotionnelle'})

@login_required
def offre_edit(request, pk):
    offre = get_object_or_404(OffrePromotion, pk=pk)
    if not user_can_manage_offre(request.user, offre):
        messages.error(request, "Vous n'avez pas l'autorisation de modifier cette offre.")
        return redirect('events:event_list')

    if request.method == 'POST':
        form = OffrePromotionForm(request.POST, instance=offre)
        if form.is_valid():
            saved_off = form.save(commit=False)
            if not saved_off.cree_par:
                saved_off.cree_par = request.user
            saved_off.save()
            messages.success(request, f"L'offre '{saved_off.titre}' a été modifiée dans la base de données.")
            return redirect('events:event_list')
    else:
        form = OffrePromotionForm(instance=offre)

    return render(request, 'events/offre_form.html', {'form': form, 'title': f"Modifier {offre.titre}"})

@login_required
def offre_delete(request, pk):
    offre = get_object_or_404(OffrePromotion, pk=pk)
    if not user_can_manage_offre(request.user, offre):
        messages.error(request, "Vous n'avez pas l'autorisation de supprimer cette offre.")
        return redirect('events:event_list')

    if request.method == 'POST':
        titre = offre.titre
        offre.delete()
        messages.success(request, f"L'offre '{titre}' a été supprimée de la base de données.")
        return redirect('events:event_list')

    return render(request, 'events/offre_confirm_delete.html', {'offre': offre})
