from django.shortcuts import render
from .models import Lieu

def home(request):
    lieux = Lieu.objects.filter(statut="ACTIF")[:8]
    return render(request, "spots/home.html", {"spots": lieux})
