"""
Module de Contrôle d'Accès et Permissions (Matrice RBAC : Visiteur, Établissement, Admin)
"""
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def is_admin(user):
    """Vérifie si l'utilisateur est administrateur système"""
    return user.is_authenticated and (user.is_staff or getattr(user, 'role', '') == 'ADMIN')

def is_etablissement_owner(user, lieu):
    """Vérifie si l'utilisateur est le propriétaire légitime et assigné de cet établissement"""
    if not user.is_authenticated:
        return False
    # Rôle établissement et assigné comme propriétaire du lieu
    return (getattr(user, 'role', '') in ['PROPRIETAIRE', 'ETABLISSEMENT']) and (lieu.proprietaire_id == user.id)

def can_manage_lieu_and_menu(user, lieu):
    """
    Règle métier stricte (RF02 / Architecture RBAC) :
    - L'Admin peut gérer tous les lieux et menus.
    - Le compte Établissement peut uniquement gérer son propre lieu et son propre menu.
    - Aucun autre utilisateur ne peut modifier les données ou le menu d'un établissement tiers.
    """
    if not user.is_authenticated:
        return False
    if is_admin(user):
        return True
    if is_etablissement_owner(user, lieu):
        return True
    return False

def admin_required(view_func):
    """Décorateur pour les vues strictement réservées à l'Administrateur"""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not is_admin(request.user):
            messages.error(request, "Accès refusé : cette action est strictement réservée à l'administrateur.")
            return redirect('spots:home')
        return view_func(request, *args, **kwargs)
    return _wrapped
