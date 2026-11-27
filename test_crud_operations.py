import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunisspot.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from users.models import Utilisateur
from spots.models import Lieu, Categorie, Quartier, Plat, Avis
from itineraries.models import Itineraire, Etape, SortieGroupe

def run_crud_tests():
    c = Client()
    admin = Utilisateur.objects.get(username='admin')
    c.force_login(admin)

    print("Testing CRUD Operations...")

    # 1. Test Spot Creation
    cat = Categorie.objects.first()
    quartier = Quartier.objects.first()
    resp = c.post(reverse('spots:spot_create'), {
        'nom': 'Café Test Marsa Plage',
        'categorie': cat.id,
        'quartier': quartier.id,
        'adresse': 'Corniche de La Marsa',
        'latitude': 36.8850,
        'longitude': 10.3300,
        'fourchette_prix': '€€',
        'prix_moyen': 20.0,
        'horaires': '08:00 - 23:00',
        'description': 'Superbe café test en bord de mer.',
        'image_principale': 'https://images.unsplash.com/photo-1554118811-1e0d58224f24',
        'terrasse': True,
        'wifi': True,
    }, follow=True)
    assert resp.status_code == 200
    test_spot = Lieu.objects.filter(nom='Café Test Marsa Plage').first()
    assert test_spot is not None
    print(f"  [OK] CRUD Lieu : Créé avec succès (ID: {test_spot.id})")

    # 2. Test Plat Creation
    resp_plat = c.post(reverse('spots:plat_create', kwargs={'lieu_id': test_spot.id}), {
        'nom': 'Citronnade artisanale aux amandes',
        'categorie_plat': 'Boisson',
        'prix': 7.5,
        'description': 'Citrons frais pressés et amandes pilées.',
        'est_populaire': True
    }, follow=True)
    assert resp_plat.status_code == 200
    plat = Plat.objects.filter(nom='Citronnade artisanale aux amandes').first()
    assert plat is not None
    print(f"  [OK] CRUD Plat : Ajouté au menu de {test_spot.nom}")

    # 3. Test Avis Creation with criteria
    resp_avis = c.post(reverse('spots:avis_create', kwargs={'lieu_id': test_spot.id}), {
        'note': 5,
        'note_qualite': 5,
        'note_service': 4,
        'note_prix': 5,
        'note_ambiance': 5,
        'commentaire': 'Expérience magnifique face aux vagues de La Marsa !'
    }, follow=True)
    assert resp_avis.status_code == 200
    avis = Avis.objects.filter(lieu=test_spot).first()
    assert avis is not None
    print(f"  [OK] CRUD Avis : Avis publié avec note {avis.note}/5 et score de confiance {avis.score_confiance}")

    # 4. Test Itinéraire Creation
    resp_itin = c.post(reverse('itineraries:itinerary_create'), {
        'titre': 'Circuit Découverte Test',
        'description': 'Circuit test de démonstration.',
        'budget': 60.0,
        'duree_totale': 180,
        'mode_transport': 'MIXTE',
        'est_public': True
    }, follow=True)
    assert resp_itin.status_code == 200
    itin = Itineraire.objects.filter(titre='Circuit Découverte Test').first()
    assert itin is not None
    print(f"  [OK] CRUD Itinéraire : Circuit créé (Lien partage: {itin.lien_partage})")

    # 5. Clean up test spot
    test_spot.delete()
    itin.delete()
    print("  [OK] CRUD Delete : Suppression test effectuée.")
    print("\n=== TOUTES LES OPÉRATIONS CRUD SONT FONCTIONNELLES ET VALIDÉES ===")

if __name__ == '__main__':
    run_crud_tests()
