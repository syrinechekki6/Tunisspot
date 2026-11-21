from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def is_admin(user):
    return user.is_authenticated and (user.is_staff or getattr(user, 'role', '') == 'ADMIN')

def is_etablissement_owner(user):
    return user.is_authenticated and getattr(user, 'role', '') == 'PROPRIETAIRE'

def can_manage_lieu_and_menu(user, lieu=None):
    if not user.is_authenticated:
        return False
    if is_admin(user):
        return True
    if lieu and lieu.proprietaire == user:
        return True
    return False

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not is_admin(request.user):
            from django.contrib import messages
            messages.error(request, "Acces administrateur requis.")
            return redirect('/')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper
