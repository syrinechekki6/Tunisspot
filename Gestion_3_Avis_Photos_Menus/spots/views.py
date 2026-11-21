from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Lieu, Avis, Photo, Plat
from .forms import AvisForm, PhotoForm, PlatForm


def home(request):
    lieux = Lieu.objects.all().order_by('-note_moyenne')[:8]
    return render(request, 'spots/home.html', {'spots': lieux})


def spot_detail(request, slug):
    lieu = get_object_or_404(Lieu, slug=slug)
    avis_list = lieu.avis.filter(statut_moderation='APPROUVE').order_by('-date_publication')
    photos = lieu.photos.filter(statut_moderation='APPROUVE')
    plats = lieu.plats.all().order_by('categorie_plat', 'prix')
    return render(request, 'spots/spot_detail.html', {
        'spot': lieu,
        'avis_list': avis_list,
        'photos': photos,
        'plats': plats,
    })


def spot_menu_detail(request, slug):
    lieu = get_object_or_404(Lieu, slug=slug)
    plats = lieu.plats.all().order_by('categorie_plat', 'prix')
    return render(request, 'spots/spot_menu.html', {'spot': lieu, 'plats': plats})


# --- AVIS CRUD ---
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
            messages.success(request, "Votre avis a ete soumis.")
            return redirect('spots:spot_detail', slug=lieu.slug)
    else:
        form = AvisForm()
    return render(request, 'spots/avis_form.html', {'form': form, 'lieu': lieu})


@login_required
def avis_edit(request, pk):
    avis = get_object_or_404(Avis, pk=pk)
    if avis.user != request.user and not request.user.is_staff:
        messages.error(request, "Acces refuse.")
        return redirect('spots:spot_detail', slug=avis.lieu.slug)
    if request.method == 'POST':
        form = AvisForm(request.POST, instance=avis)
        if form.is_valid():
            form.save()
            messages.success(request, "Avis modifie.")
            return redirect('spots:spot_detail', slug=avis.lieu.slug)
    else:
        form = AvisForm(instance=avis)
    return render(request, 'spots/avis_form.html', {'form': form, 'lieu': avis.lieu, 'avis': avis})


@login_required
def avis_delete(request, pk):
    avis = get_object_or_404(Avis, pk=pk)
    if avis.user != request.user and not request.user.is_staff:
        messages.error(request, "Acces refuse.")
        return redirect('spots:spot_detail', slug=avis.lieu.slug)
    slug = avis.lieu.slug
    if request.method == 'POST':
        avis.delete()
        messages.success(request, "Avis supprime.")
        return redirect('spots:spot_detail', slug=slug)
    return render(request, 'spots/avis_confirm_delete.html', {'avis': avis})


# --- PHOTO CRUD ---
@login_required
def photo_create(request, lieu_id):
    lieu = get_object_or_404(Lieu, pk=lieu_id)
    if request.method == 'POST':
        form = PhotoForm(request.POST)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.lieu = lieu
            photo.user = request.user
            photo.save()
            messages.success(request, "Photo ajoutee.")
            return redirect('spots:spot_detail', slug=lieu.slug)
    else:
        form = PhotoForm()
    return render(request, 'spots/photo_form.html', {'form': form, 'lieu': lieu})


@login_required
def photo_edit(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    if photo.user != request.user and not request.user.is_staff:
        messages.error(request, "Acces refuse.")
        return redirect('spots:spot_detail', slug=photo.lieu.slug)
    if request.method == 'POST':
        form = PhotoForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, "Photo modifiee.")
            return redirect('spots:spot_detail', slug=photo.lieu.slug)
    else:
        form = PhotoForm(instance=photo)
    return render(request, 'spots/photo_form.html', {'form': form, 'lieu': photo.lieu, 'photo': photo})


@login_required
def photo_delete(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    if photo.user != request.user and not request.user.is_staff:
        messages.error(request, "Acces refuse.")
        return redirect('spots:spot_detail', slug=photo.lieu.slug)
    slug = photo.lieu.slug
    if request.method == 'POST':
        photo.delete()
        messages.success(request, "Photo supprimee.")
        return redirect('spots:spot_detail', slug=slug)
    return render(request, 'spots/photo_confirm_delete.html', {'photo': photo})


# --- PLAT / MENU CRUD ---
@login_required
def plat_create(request, lieu_id):
    lieu = get_object_or_404(Lieu, pk=lieu_id)
    if request.method == 'POST':
        form = PlatForm(request.POST)
        if form.is_valid():
            plat = form.save(commit=False)
            plat.lieu = lieu
            plat.save()
            messages.success(request, f"Plat '{plat.nom}' ajoute au menu.")
            return redirect('spots:spot_menu', slug=lieu.slug)
    else:
        form = PlatForm()
    return render(request, 'spots/plat_form.html', {'form': form, 'lieu': lieu})


@login_required
def plat_edit(request, pk):
    plat = get_object_or_404(Plat, pk=pk)
    if request.method == 'POST':
        form = PlatForm(request.POST, instance=plat)
        if form.is_valid():
            form.save()
            messages.success(request, f"Plat '{plat.nom}' modifie.")
            return redirect('spots:spot_menu', slug=plat.lieu.slug)
    else:
        form = PlatForm(instance=plat)
    return render(request, 'spots/plat_form.html', {'form': form, 'lieu': plat.lieu, 'plat': plat})


@login_required
def plat_delete(request, pk):
    plat = get_object_or_404(Plat, pk=pk)
    slug = plat.lieu.slug
    if request.method == 'POST':
        plat.delete()
        messages.success(request, "Plat supprime.")
        return redirect('spots:spot_menu', slug=slug)
    return render(request, 'spots/plat_confirm_delete.html', {'plat': plat})
