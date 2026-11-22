from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Utilisateur, Preference, Badge, UserBadge, Notification
from .forms import InscriptionForm, ProfilUpdateForm, PreferenceForm

def user_register(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            # Sécurité backend stricte : seuls VISITEUR ou PROPRIETAIRE (Établissement) sont autorisés
            if user.role not in ['VISITEUR', 'PROPRIETAIRE']:
                user.role = 'VISITEUR'
            user.is_staff = False
            user.is_superuser = False
            user.points = 50 # Bonus bienvenue
            user.save()

            # Create default preference
            Preference.objects.get_or_create(user=user)

            Notification.objects.create(
                user=user,
                titre="Bienvenue sur TunisSpot ! 🇹🇳",
                message="Votre compte est activé avec 50 points de bienvenue sur votre Passeport de découverte.",
                lien="/users/profil/"
            )

            login(request, user)
            messages.success(request, f"Bienvenue {user.username} ! Votre compte a été créé avec succès et enregistré dans la base de données (+50 points).")
            return redirect('spots:home')
        else:
            messages.error(request, "Impossible de finaliser l'inscription. Veuillez corriger les erreurs indiquées ci-dessous.")
    else:
        form = InscriptionForm()

    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('spots:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Ravi de vous revoir, {user.nom or user.username} !")
            next_url = request.GET.get('next', 'spots:home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté avec succès.")
    return redirect('spots:home')

@login_required
def profile_view(request):
    """Passeport de découverte & gestion du compte"""
    user = request.user
    preference, _ = Preference.objects.get_or_create(user=user)

    if request.method == 'POST':
        if 'update_profil' in request.POST:
            p_form = ProfilUpdateForm(request.POST, request.FILES, instance=user)
            if p_form.is_valid():
                p_form.save()
                messages.success(request, "Votre profil et photo ont été mis à jour.")
                return redirect('users:profil')
        elif 'update_pref' in request.POST:
            pref_form = PreferenceForm(request.POST, instance=preference)
            if pref_form.is_valid():
                pref_form.save()
                messages.success(request, "Vos préférences de sortie ont été enregistrées.")
                return redirect('users:profil')

    p_form = ProfilUpdateForm(instance=user)
    pref_form = PreferenceForm(instance=preference)

    all_badges = Badge.objects.all()
    user_badges_ids = user.badges.values_list('badge_id', flat=True)

    # Check for unlocking new badges
    for b in all_badges:
        if b.id not in user_badges_ids and user.points >= b.points_requis:
            UserBadge.objects.create(user=user, badge=b)
            Notification.objects.create(
                user=user,
                titre=f"Nouveau Badge Débloqué : {b.nom} !",
                message=f"Félicitations, vous avez débloqué le badge '{b.nom}' ({b.points_requis} pts).",
                lien="/users/profil/"
            )

    return render(request, 'users/profile.html', {
        'user': user,
        'p_form': p_form,
        'pref_form': pref_form,
        'all_badges': all_badges,
        'user_badges_ids': user_badges_ids,
        'points_needed_for_next': max(0, 250 - user.points) if user.points < 250 else max(0, 500 - user.points),
    })

@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-date_envoi')
    # Mark all as read
    notifs.filter(est_lue=False).update(est_lue=True)
    return render(request, 'users/notifications.html', {'notifications': notifs})
