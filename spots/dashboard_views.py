from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from spots.models import Lieu, Avis, Photo, Revendication, Signalement, Categorie
from users.models import Utilisateur, Notification
from events.models import StatistiqueFiche, OffrePromotion

def is_admin_or_moderator(user):
    return user.is_authenticated and (user.is_staff or user.role in ['ADMIN', 'MODERATEUR'])

@login_required
@user_passes_test(is_admin_or_moderator)
def admin_dashboard(request):
    """Back-office Administrateur & Modération (RF30)"""
    total_spots = Lieu.objects.count()
    total_users = Utilisateur.objects.count()
    total_avis = Avis.objects.count()
    signalements_en_attente = Signalement.objects.filter(statut='NOUVEAU').count()
    revendications_en_attente = Revendication.objects.filter(statut='EN_ATTENTE').count()

    avis_en_attente = Avis.objects.filter(statut_moderation='EN_ATTENTE')
    lieux_en_attente = Lieu.objects.filter(statut='EN_ATTENTE').order_by('-date_creation')
    lieux_en_attente_count = lieux_en_attente.count()
    signalements = Signalement.objects.all().order_by('-date_signalement')[:10]
    revendications = Revendication.objects.filter(statut='EN_ATTENTE').order_by('-date_demande')
    recents_lieux = Lieu.objects.filter(statut='ACTIF').order_by('-date_creation')[:6]

    return render(request, 'dashboard/admin_dashboard.html', {
        'total_spots': total_spots,
        'total_users': total_users,
        'total_avis': total_avis,
        'signalements_en_attente': signalements_en_attente,
        'revendications_en_attente': revendications_en_attente,
        'lieux_en_attente': lieux_en_attente,
        'lieux_en_attente_count': lieux_en_attente_count,
        'avis_en_attente': avis_en_attente,
        'signalements': signalements,
        'revendications': revendications,
        'recents_lieux': recents_lieux,
    })

# VALIDATION DES LIEUX PAR L'ADMINISTRATEUR (WORKFLOW VISITEUR -> ADMIN)
@login_required
@user_passes_test(is_admin_or_moderator)
def admin_valider_lieu(request, lieu_id, action):
    """
    Workflow validation de lieu :
    - accepter : devient public (statut='ACTIF'), notifie l'auteur et crédite 30 pts
    - refuser : supprime automatiquement le lieu et notifie l'auteur
    """
    lieu = get_object_or_404(Lieu, pk=lieu_id)
    if action == 'accepter':
        lieu.statut = 'ACTIF'
        lieu.save()
        if lieu.proprietaire:
            lieu.proprietaire.points += 30
            lieu.proprietaire.save(update_fields=['points'])
            Notification.objects.create(
                user=lieu.proprietaire,
                titre="Spot validé avec succès ! 🎉",
                message=f"Félicitations ! Votre lieu '{lieu.nom}' a été approuvé par l'administrateur et est maintenant public (+30 pts).",
                lien=f"/spot/{lieu.slug}/"
            )
        messages.success(request, f"Le spot '{lieu.nom}' a été accepté et est désormais public.")
    elif action == 'refuser':
        nom = lieu.nom
        if lieu.proprietaire:
            Notification.objects.create(
                user=lieu.proprietaire,
                titre="Proposition de lieu non retenue",
                message=f"Votre proposition de lieu '{nom}' n'a pas été retenue par l'administration de TunisSpot.",
                lien="/users/profil/"
            )
        lieu.delete()
        messages.warning(request, f"La proposition de lieu '{nom}' a été refusée et supprimée automatiquement.")
    return redirect('dashboard:admin_dashboard')

# GESTION DES UTILISATEURS (ADMINISTRATION & SUPPRESSION)
@login_required
@user_passes_test(is_admin_or_moderator)
def admin_users(request):
    """Consultation et recherche de la liste des utilisateurs de la plateforme"""
    users_qs = Utilisateur.objects.all().order_by('-date_inscription')
    
    q = request.GET.get('q')
    if q:
        from django.db.models import Q
        users_qs = users_qs.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(nom__icontains=q)
        )

    role_filter = request.GET.get('role')
    if role_filter:
        users_qs = users_qs.filter(role=role_filter)

    return render(request, 'dashboard/admin_users.html', {
        'users_list': users_qs,
        'total_count': users_qs.count(),
        'query': q,
        'selected_role': role_filter,
    })

@login_required
@user_passes_test(is_admin_or_moderator)
def admin_user_delete(request, user_id):
    """Suppression sécurisée d'un utilisateur par l'administrateur avec confirmation"""
    user_to_delete = get_object_or_404(Utilisateur, pk=user_id)
    
    # Sécurité : empêcher l'administrateur de supprimer son propre compte
    if user_to_delete == request.user:
        messages.error(request, "Action interdite : vous ne pouvez pas supprimer votre propre compte administrateur en cours d'utilisation.")
        return redirect('dashboard:admin_users')

    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f"Le compte utilisateur '{username}' a été supprimé définitivement de la base de données.")
        return redirect('dashboard:admin_users')

    return render(request, 'dashboard/user_confirm_delete.html', {
        'user_to_delete': user_to_delete,
    })

@login_required
@user_passes_test(is_admin_or_moderator)
def moderer_avis(request, avis_id, action):
    avis = get_object_or_404(Avis, pk=avis_id)
    if action == 'approuver':
        avis.statut_moderation = 'APPROUVE'
        messages.success(request, f"L'avis de {avis.user.username} a été approuvé.")
    elif action == 'rejeter':
        avis.statut_moderation = 'REJETE'
        messages.warning(request, f"L'avis de {avis.user.username} a été rejeté.")
    avis.save()
    avis.lieu.calculer_note_moyenne()
    return redirect('dashboard:admin_dashboard')

@login_required
@user_passes_test(is_admin_or_moderator)
def traiter_revendication(request, rev_id, action):
    rev = get_object_or_404(Revendication, pk=rev_id)
    if action == 'valider':
        rev.statut = 'APPROUVEE'
        rev.lieu.proprietaire = rev.user
        rev.lieu.save(update_fields=['proprietaire'])
        
        # Passer l'utilisateur en rôle propriétaire si besoin
        rev.user.role = 'PROPRIETAIRE'
        rev.user.save(update_fields=['role'])

        Notification.objects.create(
            user=rev.user,
            titre="Revendication approuvée !",
            message=f"Félicitations, vous êtes désormais le gestionnaire officiel de la fiche {rev.lieu.nom}.",
            lien=f"/spot/{rev.lieu.slug}/"
        )
        messages.success(request, f"La revendication pour {rev.lieu.nom} a été validée. {rev.user.username} est maintenant propriétaire.")
    elif action == 'rejeter':
        rev.statut = 'REJETEE'
        messages.info(request, "La demande de revendication a été rejetée.")
    rev.save()
    return redirect('dashboard:admin_dashboard')

@login_required
def owner_dashboard(request):
    """Tableau de bord Propriétaire d'Établissement (Module 6)"""
    mes_lieux = Lieu.objects.filter(proprietaire=request.user)
    if not mes_lieux.exists() and not request.user.is_staff:
        # Check if user has pending claims
        pending_claim = Revendication.objects.filter(user=request.user, statut='EN_ATTENTE').first()
        return render(request, 'dashboard/owner_dashboard.html', {
            'aucun_lieu': True,
            'pending_claim': pending_claim
        })

    # Stats aggregations
    stats = StatistiqueFiche.objects.filter(lieu__in=mes_lieux)
    total_vues = stats.aggregate(Sum('nombre_vues'))['nombre_vues__sum'] or 0
    total_itineraires = stats.aggregate(Sum('nombre_clics_itineraire'))['nombre_clics_itineraire__sum'] or 0
    total_favoris = stats.aggregate(Sum('nombre_ajouts_favoris'))['nombre_ajouts_favoris__sum'] or 0
    total_menus = stats.aggregate(Sum('nombre_clics_menu'))['nombre_clics_menu__sum'] or 0

    return render(request, 'dashboard/owner_dashboard.html', {
        'mes_lieux': mes_lieux,
        'total_vues': total_vues,
        'total_itineraires': total_itineraires,
        'total_favoris': total_favoris,
        'total_menus': total_menus,
        'aucun_lieu': False
    })
