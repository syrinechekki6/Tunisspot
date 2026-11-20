from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import random
from .models import Lieu


def home(request):
    lieux = Lieu.objects.filter(statut="ACTIF")[:8]
    return render(request, "spots/home.html", {"spots": lieux})


def spot_list(request):
    lieux = Lieu.objects.filter(statut="ACTIF")
    quartier = request.GET.get('quartier')
    pepite = request.GET.get('pepite')
    if quartier:
        lieux = lieux.filter(quartier=quartier)
    if pepite:
        lieux = lieux.filter(pepite=True)
    return render(request, "spots/spot_list.html", {"spots": lieux})


def random_spot(request):
    lieux = list(Lieu.objects.filter(statut="ACTIF"))
    if lieux:
        lieu = random.choice(lieux)
        return render(request, "spots/random_spot.html", {"spot": lieu})
    return render(request, "spots/random_spot.html", {"spot": None})


@login_required
def spot_create(request):
    return render(request, "spots/spot_create.html")

