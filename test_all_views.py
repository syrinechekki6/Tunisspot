import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunisspot.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from users.models import Utilisateur
from spots.models import Lieu

def run_tests():
    c = Client()
    print("Testing URLs...")

    spot = Lieu.objects.first()

    urls_to_test = [
        (reverse('spots:home'), 200, "Page d'accueil"),
        (reverse('spots:spot_list'), 200, "Catalogue des spots"),
        (reverse('spots:random_spot'), 200, "Le Hasard (Win Tokhrej feature)"),
        (reverse('transports:comparator'), 200, "Comparateur multimodal"),
        (reverse('itineraries:itinerary_list'), 200, "Liste des itinéraires"),
        ('/itineraires/generateur/?generate=1&duree=JOURNEE&budget=MOYEN&ambiance=ROMANTIQUE', 200, "Générateur de Journée Parfaite"),
        (reverse('events:event_list'), 200, "Agenda & Bons plans"),
        (reverse('users:login'), 200, "Page de connexion"),
        (reverse('users:register'), 200, "Page d'inscription"),
    ]

    if spot:
        urls_to_test.append((reverse('spots:spot_detail', kwargs={'slug': spot.slug}), 200, f"Fiche détaillée {spot.nom}"))

    all_passed = True
    for url, expected_code, name in urls_to_test:
        response = c.get(url, follow=True)
        status = response.status_code
        if status == expected_code:
            print(f"  [OK] {name} ({url}) -> HTTP {status}")
        else:
            print(f"  [FAIL] {name} ({url}) -> HTTP {status} (attendu {expected_code})")
            all_passed = False

    # Authenticated user tests
    admin = Utilisateur.objects.filter(username='admin').first()
    if admin:
        c.force_login(admin)
        auth_urls = [
            (reverse('users:profil'), 200, "Passeport de découverte"),
            (reverse('itineraries:favoris'), 200, "Mes favoris"),
            (reverse('itineraries:group_trips'), 200, "Sorties de groupe"),
            (reverse('dashboard:admin_dashboard'), 200, "Tableau de bord Admin / Modération"),
            (reverse('dashboard:owner_dashboard'), 200, "Tableau de bord Propriétaire"),
        ]
        for url, expected_code, name in auth_urls:
            response = c.get(url, follow=True)
            status = response.status_code
            if status == expected_code:
                print(f"  [OK - Auth] {name} ({url}) -> HTTP {status}")
            else:
                print(f"  [FAIL - Auth] {name} ({url}) -> HTTP {status} (attendu {expected_code})")
                all_passed = False

    if all_passed:
        print("\n=== TOUS LES TESTS SONT VALIDES AVEC SUCCÈS (100% OK) ===")
    else:
        print("\n=== CERTAINS TESTS ONT ÉCHOUÉ ===")

if __name__ == '__main__':
    run_tests()
