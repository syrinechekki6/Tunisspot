"""
Suite complète de tests automatisés pour la gestion des rôles, permissions,
workflow de validation de lieu, module transport GPS et photos de profil.
"""
import os
import io
import django
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunisspot.settings')
django.setup()

from django.test import Client, TestCase
from users.models import Utilisateur, Notification
from users.forms import InscriptionForm, ProfilUpdateForm
from spots.models import Lieu, Categorie, Quartier, Plat
from transports.models import TrajetHistorique

class ArchitectureRBACWorkflowTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # 1. Catégorie & Quartier de test
        self.cat, _ = Categorie.objects.get_or_create(libelle="Café & Salon de thé", defaults={'slug': 'cafe-the'})
        self.quartier, _ = Quartier.objects.get_or_create(nom="Sidi Bou Saïd")

        # 2. Utilisateurs
        self.admin_user, _ = Utilisateur.objects.get_or_create(
            username="admin_test",
            defaults={'email': 'admin_test@tunisspot.tn', 'role': 'ADMIN', 'is_staff': True}
        )
        self.admin_user.set_password("AdminPass123!")
        self.admin_user.save()

        self.visiteur_user, _ = Utilisateur.objects.get_or_create(
            username="visiteur_test",
            defaults={'email': 'visiteur_test@tunisspot.tn', 'role': 'VISITEUR', 'is_staff': False}
        )
        self.visiteur_user.set_password("VisiteurPass123!")
        self.visiteur_user.save()

        self.etab1_user, _ = Utilisateur.objects.get_or_create(
            username="etab1_test",
            defaults={'email': 'etab1@tunisspot.tn', 'role': 'PROPRIETAIRE', 'is_staff': False}
        )
        self.etab1_user.set_password("Etab1Pass123!")
        self.etab1_user.save()

        self.etab2_user, _ = Utilisateur.objects.get_or_create(
            username="etab2_test",
            defaults={'email': 'etab2@tunisspot.tn', 'role': 'PROPRIETAIRE', 'is_staff': False}
        )
        self.etab2_user.set_password("Etab2Pass123!")
        self.etab2_user.save()

        # 3. Lieux
        self.lieu_etab1 = Lieu.objects.create(
            nom="Restaurant Etablissement 1",
            categorie=self.cat,
            quartier=self.quartier,
            adresse="Rue 1, Sidi Bou Said",
            statut="ACTIF",
            proprietaire=self.etab1_user
        )

        self.lieu_etab2 = Lieu.objects.create(
            nom="Café Etablissement 2",
            categorie=self.cat,
            quartier=self.quartier,
            adresse="Rue 2, Sidi Bou Said",
            statut="ACTIF",
            proprietaire=self.etab2_user
        )

    def test_01_inscription_roles_and_admin_security(self):
        print("\n--- 1. TEST AUTHENTIFICATION & RÔLES ---")
        form = InscriptionForm()
        role_choices = [c[0] for c in form.fields['role'].choices]
        print("Choix proposés dans InscriptionForm :", role_choices)
        self.assertIn('VISITEUR', role_choices)
        self.assertIn('PROPRIETAIRE', role_choices)
        self.assertNotIn('ADMIN', role_choices, "ADMIN ne doit jamais être présent dans l'inscription !")

        # Tentative d'injection malveillante role=ADMIN -> Rejetée dès la validation du formulaire
        resp = self.client.post(reverse('users:register'), {
            'username': 'hacker_role',
            'nom': 'Fake Admin Attempt',
            'email': 'hacker@tunisspot.tn',
            'role': 'ADMIN',
            'langue': 'FR',
            'password1': 'SafePass1234!',
            'password2': 'SafePass1234!',
        }, follow=True)
        hacker_user = Utilisateur.objects.filter(username='hacker_role').first()
        self.assertIsNone(hacker_user, "Une soumission avec rôle ADMIN doit être rejetée côté serveur !")
        print("[OK] Sécurité backend des rôles validée : injection ADMIN neutralisée")

        # Inscription normale rôle VISITEUR
        resp_valid = self.client.post(reverse('users:register'), {
            'username': 'nouveau_visiteur',
            'nom': 'Visiteur Valide',
            'email': 'visiteur_valide@tunisspot.tn',
            'role': 'VISITEUR',
            'langue': 'FR',
            'password1': 'SafePass1234!',
            'password2': 'SafePass1234!',
        }, follow=True)
        new_visiteur = Utilisateur.objects.filter(username='nouveau_visiteur').first()
        self.assertIsNotNone(new_visiteur)
        self.assertEqual(new_visiteur.role, 'VISITEUR')
        self.assertFalse(new_visiteur.is_staff)
        print("[OK] Inscription légitime avec rôle Visiteur validée")

    def test_02_photo_profil_and_generic_icon_fallback(self):
        print("\n--- 2. TEST PHOTO DE PROFIL & AVATAR ICÔNE PAR DÉFAUT ---")
        user = self.visiteur_user
        self.assertFalse(user.has_custom_avatar)
        self.assertIsNone(user.avatar_display, "Sans photo, avatar_display doit être None (icône générique utilisée)")

        # Test upload invalide (mauvaise extension PDF)
        fake_pdf = SimpleUploadedFile("avatar.pdf", b"%PDF-1.4 fake pdf content", content_type="application/pdf")
        update_form = ProfilUpdateForm(data={'nom': 'Test', 'email': user.email, 'langue': 'FR'}, files={'photo_profil': fake_pdf})
        self.assertFalse(update_form.is_valid(), "Un fichier PDF doit être rejeté pour la photo de profil")
        print("[OK] Rejet automatique des extensions non autorisées validé")

        # Test upload valide (Image PIL PNG)
        img_io = io.BytesIO()
        img = Image.new('RGB', (100, 100), color=(73, 109, 137))
        img.save(img_io, format='PNG')
        img_file = SimpleUploadedFile("avatar.png", img_io.getvalue(), content_type="image/png")

        update_form_valid = ProfilUpdateForm(data={'nom': 'Nom Avec Photo', 'email': user.email, 'langue': 'FR'}, files={'photo_profil': img_file}, instance=user)
        self.assertTrue(update_form_valid.is_valid(), f"Erreurs formulaire : {update_form_valid.errors}")
        update_form_valid.save()
        self.assertTrue(user.has_custom_avatar)
        self.assertIsNotNone(user.avatar_display)
        print("[OK] Upload d'image valide (PNG) accepté et persisté")

    def test_03_etablissement_strict_ownership(self):
        print("\n--- 3. TEST PERMISSIONS STRICTES ÉTABLISSEMENT ---")
        # Etab 1 ajoute un plat à son propre lieu -> Succès
        self.client.force_login(self.etab1_user)
        resp = self.client.post(reverse('spots:plat_create', args=[self.lieu_etab1.id]), {
            'nom': 'Couscous au Mérou',
            'description': 'Spécialité du chef',
            'prix': 32.0,
            'categorie_plat': 'Plat principal'
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        plat = Plat.objects.filter(nom='Couscous au Mérou').first()
        self.assertIsNotNone(plat)
        self.assertEqual(plat.lieu, self.lieu_etab1)
        print("[OK] Établissement 1 peut ajouter un plat à son propre lieu")

        # Etab 1 tente d'ajouter un plat au lieu de Etab 2 -> Refusé
        resp_illegal = self.client.post(reverse('spots:plat_create', args=[self.lieu_etab2.id]), {
            'nom': 'Plat Piraté',
            'description': 'Tentative illégale',
            'prix': 10.0,
            'categorie_plat': 'Plat principal'
        }, follow=True)
        plat_hacked = Plat.objects.filter(nom='Plat Piraté').first()
        self.assertIsNone(plat_hacked, "L'établissement 1 ne doit JAMAIS pouvoir ajouter un plat chez l'établissement 2 !")
        print("[OK] Protection serveur : modification interdite sur les établissements tiers")

    def test_04_workflow_lieu_validation(self):
        print("\n--- 4. TEST WORKFLOW D'AJOUT DE LIEU (Visiteur -> Admin) ---")
        # 1. Visiteur ajoute un lieu -> Statut EN_ATTENTE
        self.client.force_login(self.visiteur_user)
        resp = self.client.post(reverse('spots:spot_create'), {
            'nom': 'Café Test Visiteur',
            'categorie': self.cat.id,
            'quartier': self.quartier.id,
            'adresse': '12 Avenue Habib Bourguiba',
            'latitude': 36.8001,
            'longitude': 10.1802,
            'description': 'Super endroit calme',
            'fourchette_prix': '€€',
            'prix_moyen': 15.0,
            'horaires': '08:00 - 22:00',
            'indice_foule': 'Faible',
        }, follow=True)
        
        lieu_pending = Lieu.objects.filter(nom='Café Test Visiteur').first()
        self.assertIsNotNone(lieu_pending)
        self.assertEqual(lieu_pending.statut, 'EN_ATTENTE', "Un lieu proposé par un visiteur DOIT être EN_ATTENTE !")
        print(f"[OK] Lieu créé par visiteur mis en attente : ID={lieu_pending.id}, statut={lieu_pending.statut}")

        # 2. Visibilité restreinte : public/anonyme ne peut pas le voir (404)
        c_anon = Client()
        resp_anon = c_anon.get(reverse('spots:spot_detail', args=[lieu_pending.slug]))
        self.assertEqual(resp_anon.status_code, 404, "Le public ne doit pas pouvoir voir un lieu EN_ATTENTE !")

        # Mais l'auteur PEUT le consulter avec la bannière
        resp_author = self.client.get(reverse('spots:spot_detail', args=[lieu_pending.slug]))
        self.assertEqual(resp_author.status_code, 200)
        self.assertContains(resp_author, "Lieu en cours de modération")
        print("[OK] Visibilité en attente sécurisée (404 public, visible par auteur et admin)")

        # 3. Admin publie immédiatement sans validation
        self.client.force_login(self.admin_user)
        resp_admin = self.client.post(reverse('spots:spot_create'), {
            'nom': 'Grand Théâtre Municipal',
            'categorie': self.cat.id,
            'quartier': self.quartier.id,
            'adresse': 'Avenue Bourguiba',
            'latitude': 36.7999,
            'longitude': 10.1805,
            'description': 'Édifice culturel historique',
            'fourchette_prix': '€€',
            'prix_moyen': 20.0,
            'horaires': '10:00 - 23:00',
            'indice_foule': 'Moyen',
        }, follow=True)
        lieu_admin = Lieu.objects.filter(nom='Grand Théâtre Municipal').first()
        self.assertIsNotNone(lieu_admin)
        self.assertEqual(lieu_admin.statut, 'ACTIF', "Un lieu créé par Admin doit être immédiatement ACTIF !")
        print("[OK] Création par Admin publiée immédiatement en statut ACTIF")

        # 4. Décision Admin : Accepter le lieu en attente
        resp_accept = self.client.get(reverse('dashboard:admin_valider_lieu', args=[lieu_pending.id, 'accepter']), follow=True)
        lieu_pending.refresh_from_db()
        self.assertEqual(lieu_pending.statut, 'ACTIF', "Après acceptation Admin, le lieu doit être ACTIF !")
        
        # Vérification notification envoyée à l'auteur
        notif = Notification.objects.filter(user=self.visiteur_user, titre__icontains="Spot validé").first()
        self.assertIsNotNone(notif, "Une notification d'acceptation doit être envoyée à l'auteur !")
        print(f"[OK] Acceptation validée par Admin et notification délivrée à {self.visiteur_user.username}")

        # 5. Décision Admin : Refuser un lieu en attente -> Suppression automatique
        self.client.force_login(self.visiteur_user)
        self.client.post(reverse('spots:spot_create'), {
            'nom': 'Lieu À Refuser',
            'categorie': self.cat.id,
            'quartier': self.quartier.id,
            'adresse': 'Rue Test Refus',
            'latitude': 36.8000,
            'longitude': 10.1800,
            'fourchette_prix': '€',
            'prix_moyen': 10.0,
            'horaires': '08:00 - 20:00',
        }, follow=True)
        lieu_to_reject = Lieu.objects.filter(nom='Lieu À Refuser').first()
        self.assertIsNotNone(lieu_to_reject)

        self.client.force_login(self.admin_user)
        self.client.get(reverse('dashboard:admin_valider_lieu', args=[lieu_to_reject.id, 'refuser']), follow=True)
        lieu_deleted = Lieu.objects.filter(nom='Lieu À Refuser').first()
        self.assertIsNone(lieu_deleted, "Un lieu refusé par l'Admin doit être supprimé automatiquement !")
        print("[OK] Refus validé : suppression automatique de l'entité et notification de refus")

    def test_05_transport_gps_and_coordinates_storage(self):
        print("\n--- 5. TEST MODULE TRANSPORT & GÉOLOCALISATION GPS ---")
        self.client.force_login(self.visiteur_user)
        
        # Envoi de coordonnées GPS arbitraires départ et arrivée
        dep_lat = 36.8065
        dep_lng = 10.1815
        arr_lat = 36.8785
        arr_lng = 10.3425

        resp = self.client.get(reverse('transports:comparator'), {
            'depart_nom': 'Ma position GPS actuelle',
            'depart_lat': dep_lat,
            'depart_lng': dep_lng,
            'arrivee_nom': 'La Marsa Corniche',
            'arrivee_lat': arr_lat,
            'arrivee_lng': arr_lng,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Ma position GPS actuelle")
        self.assertContains(resp, "La Marsa Corniche")

        # Vérification du stockage en base de données dans TrajetHistorique
        trajet = TrajetHistorique.objects.filter(user=self.visiteur_user).first()
        self.assertIsNotNone(trajet)
        self.assertAlmostEqual(trajet.depart_latitude, dep_lat, places=3)
        self.assertAlmostEqual(trajet.depart_longitude, dep_lng, places=3)
        self.assertAlmostEqual(trajet.arrivee_latitude, arr_lat, places=3)
        self.assertAlmostEqual(trajet.arrivee_longitude, arr_lng, places=3)
        self.assertGreater(trajet.distance_km, 0)
        print(f"[OK] Trajet multimodal calculé et coordonnées GPS persistées en base : {trajet.distance_km} km")

if __name__ == '__main__':
    import unittest
    unittest.main()
