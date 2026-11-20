from django.shortcuts import render


def comparator(request):
    return render(request, 'transports/comparator.html')
