from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def generator(request):
    return render(request, 'itineraries/generator.html')


@login_required
def favoris(request):
    return render(request, 'itineraries/favoris.html')


@login_required
def my_itineraries(request):
    return render(request, 'itineraries/my_itineraries.html')


@login_required
def group_trips(request):
    return render(request, 'itineraries/group_trips.html')
