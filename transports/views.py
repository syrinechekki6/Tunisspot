from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from spots.models import Lieu
from .models import MoyenTransport, Ligne, Station, TrajetHistorique
import math
import json

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def comparator(request):
    lieux = Lieu.objects.filter(statut='ACTIF').order_by('nom')
    lignes = Ligne.objects.prefetch_related('stations').all()
    stations = Station.objects.all().order_by('type', 'ordre')

    depart_lieu_id = request.GET.get('depart')
    arrivee_lieu_id = request.GET.get('arrivee')

    # Coordonnées et saisies manuelles ou GPS (RF05 Transport)
    depart_nom = request.GET.get('depart_nom', '')
    depart_lat = request.GET.get('depart_lat')
    depart_lng = request.GET.get('depart_lng')

    arrivee_nom = request.GET.get('arrivee_nom', '')
    arrivee_lat = request.GET.get('arrivee_lat')
    arrivee_lng = request.GET.get('arrivee_lng')

    resultats = []
    depart_spot = None
    arrivee_spot = None
    distance_km = 0.0

    dep_lat, dep_lng, dep_label = None, None, None
    arr_lat, arr_lng, arr_label = None, None, None

    # 1. Résolution du point de départ (Lieu du catalogue OU GPS / Carte / Saisie manuelle)
    if depart_lieu_id:
        try:
            depart_spot = Lieu.objects.get(pk=depart_lieu_id, statut='ACTIF')
            dep_lat = depart_spot.latitude
            dep_lng = depart_spot.longitude
            dep_label = depart_spot.nom
        except Lieu.DoesNotExist:
            pass
    elif depart_lat and depart_lng:
        try:
            dep_lat = float(depart_lat)
            dep_lng = float(depart_lng)
            dep_label = depart_nom.strip() or f"Position ({dep_lat:.4f}, {dep_lng:.4f})"
        except ValueError:
            pass

    # 2. Résolution du point d'arrivée (Lieu du catalogue OU Carte / Saisie manuelle)
    if arrivee_lieu_id:
        try:
            arrivee_spot = Lieu.objects.get(pk=arrivee_lieu_id, statut='ACTIF')
            arr_lat = arrivee_spot.latitude
            arr_lng = arrivee_spot.longitude
            arr_label = arrivee_spot.nom
        except Lieu.DoesNotExist:
            pass
    elif arrivee_lat and arrivee_lng:
        try:
            arr_lat = float(arrivee_lat)
            arr_lng = float(arrivee_lng)
            arr_label = arrivee_nom.strip() or f"Destination ({arr_lat:.4f}, {arr_lng:.4f})"
        except ValueError:
            pass

    # 3. Calcul multimodal si les 2 coordonnées sont disponibles
    if dep_lat is not None and dep_lng is not None and arr_lat is not None and arr_lng is not None:
        distance_km = calculate_distance(dep_lat, dep_lng, arr_lat, arr_lng)
        if distance_km < 0.5:
            distance_km = 0.8

        moyens = MoyenTransport.objects.all()
        for m in moyens:
            vitesse = max(m.vitesse_moyenne_kmh, 4.0)
            duree_minutes = int((distance_km / vitesse) * 60) + (5 if m.nom in ['TGM', 'Métro léger'] else 2)

            if 'pied' in m.nom.lower():
                cout = 0.0
                reco = "Le plus écologique 🌿"
            elif 'tgm' in m.nom.lower() or 'métro' in m.nom.lower():
                cout = round(m.tarif_base_tnd + (distance_km * m.tarif_km_tnd), 3)
                reco = "Le plus économique 💰"
            elif 'taxi' in m.nom.lower():
                cout = round(m.tarif_base_tnd + (distance_km * m.tarif_km_tnd) + (duree_minutes * 0.05), 2)
                reco = "Le plus rapide & direct ⚡"
            else:
                cout = round(m.tarif_base_tnd + (distance_km * m.tarif_km_tnd), 2)
                reco = "Autonome"

            resultats.append({
                'moyen': m,
                'duree_minutes': duree_minutes,
                'cout_estime_tnd': cout,
                'confort': m.confort,
                'recommandation': reco
            })

        if request.user.is_authenticated and resultats:
            TrajetHistorique.objects.create(
                user=request.user,
                depart_nom=dep_label,
                depart_latitude=dep_lat,
                depart_longitude=dep_lng,
                arrivee_nom=arr_label,
                arrivee_latitude=arr_lat,
                arrivee_longitude=arr_lng,
                arrivee_lieu=arrivee_spot,
                distance_km=distance_km,
                duree_minutes=resultats[0]['duree_minutes'],
                mode_choisi="Comparateur Multimodal",
                cout_estime_tnd=resultats[0]['cout_estime_tnd']
            )

    stations_data = [
        {
            'nom': s.nom,
            'type': s.type,
            'lat': float(s.latitude),
            'lng': float(s.longitude),
            'ligne': s.ligne.nom if s.ligne else ''
        }
        for s in stations
    ]
    lieux_data = [
        {
            'id': l.id,
            'nom': l.nom,
            'quartier': l.quartier.nom if l.quartier else 'Tunis',
            'lat': float(l.latitude),
            'lng': float(l.longitude)
        }
        for l in lieux
    ]
    route_data = {
        'dep_lat': float(dep_lat) if dep_lat is not None else None,
        'dep_lng': float(dep_lng) if dep_lng is not None else None,
        'dep_label': dep_label or '',
        'arr_lat': float(arr_lat) if arr_lat is not None else None,
        'arr_lng': float(arr_lng) if arr_lng is not None else None,
        'arr_label': arr_label or ''
    }

    return render(request, 'transports/comparator.html', {
        'lieux': lieux,
        'lignes': lignes,
        'stations': stations,
        'depart_spot': depart_spot,
        'arrivee_spot': arrivee_spot,
        'dep_lat': dep_lat,
        'dep_lng': dep_lng,
        'dep_label': dep_label,
        'arr_lat': arr_lat,
        'arr_lng': arr_lng,
        'arr_label': arr_label,
        'distance_km': distance_km,
        'resultats': resultats,
        'stations_json': json.dumps(stations_data),
        'lieux_json': json.dumps(lieux_data),
        'route_json': json.dumps(route_data),
    })

# CRUD STATIONS (Ajouter, Modifier, Supprimer)
@login_required
def station_create(request):
    if not (request.user.is_staff or request.user.role == 'ADMIN'):
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('transports:comparator')

    lignes = Ligne.objects.all()
    if request.method == 'POST':
        nom = request.POST.get('nom')
        stype = request.POST.get('type')
        ligne_id = request.POST.get('ligne')
        lat = float(request.POST.get('latitude', 36.8065))
        lng = float(request.POST.get('longitude', 10.1815))
        
        ligne = Ligne.objects.filter(pk=ligne_id).first() if ligne_id else None
        st = Station.objects.create(nom=nom, type=stype, ligne=ligne, latitude=lat, longitude=lng)
        messages.success(request, f"La station '{st.nom}' a été créée avec succès dans la base de données.")
        return redirect('transports:comparator')

    return render(request, 'transports/station_form.html', {'lignes': lignes, 'title': 'Ajouter une nouvelle station'})

@login_required
def station_edit(request, pk):
    if not (request.user.is_staff or request.user.role == 'ADMIN'):
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('transports:comparator')

    station = get_object_or_404(Station, pk=pk)
    lignes = Ligne.objects.all()
    if request.method == 'POST':
        station.nom = request.POST.get('nom')
        station.type = request.POST.get('type')
        ligne_id = request.POST.get('ligne')
        station.ligne = Ligne.objects.filter(pk=ligne_id).first() if ligne_id else None
        station.latitude = float(request.POST.get('latitude', station.latitude))
        station.longitude = float(request.POST.get('longitude', station.longitude))
        station.save()
        messages.success(request, f"La station '{station.nom}' a été modifiée dans la base de données.")
        return redirect('transports:comparator')

    return render(request, 'transports/station_form.html', {'station': station, 'lignes': lignes, 'title': f"Modifier {station.nom}"})

@login_required
def station_delete(request, pk):
    if not (request.user.is_staff or request.user.role == 'ADMIN'):
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('transports:comparator')

    station = get_object_or_404(Station, pk=pk)
    if request.method == 'POST':
        nom = station.nom
        station.delete()
        messages.success(request, f"La station '{nom}' a été supprimée de la base de données.")
        return redirect('transports:comparator')

    return render(request, 'transports/station_confirm_delete.html', {'station': station})
