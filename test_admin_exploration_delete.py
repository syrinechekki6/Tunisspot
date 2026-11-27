import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunisspot.settings')
django.setup()

from django.test import Client, TestCase
from django.urls import reverse
from users.models import Utilisateur
from spots.models import Lieu, Categorie, Quartier
from events.models import Evenement, OffrePromotion
from django.utils import timezone

class AdminExplorationDeleteTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat, _ = Categorie.objects.get_or_create(libelle="Café & Salon", defaults={'slug': 'cafe-salon'})
        self.quartier, _ = Quartier.objects.get_or_create(nom="Carthage")

        self.admin_user, _ = Utilisateur.objects.get_or_create(
            username="admin_explor",
            defaults={'email': 'admin_explor@tunisspot.tn', 'role': 'ADMIN', 'is_staff': True}
        )
        self.visiteur_user, _ = Utilisateur.objects.get_or_create(
            username="visiteur_explor",
            defaults={'email': 'visiteur_explor@tunisspot.tn', 'role': 'VISITEUR', 'is_staff': False}
        )

        self.lieu = Lieu.objects.create(
            nom="Lieu Test Exploration",
            categorie=self.cat,
            quartier=self.quartier,
            adresse="Avenue Habib Bourguiba, Carthage",
            statut="ACTIF"
        )

        self.event = Evenement.objects.create(
            lieu=self.lieu,
            titre="Concert Test Exploration",
            description="Super concert live",
            date_debut=timezone.now(),
            date_fin=timezone.now() + timezone.timedelta(hours=3),
            cree_par=self.visiteur_user
        )

        self.offre = OffrePromotion.objects.create(
            lieu=self.lieu,
            titre="Offre Promo Test Exploration",
            description="Réduction 20%",
            reduction_pourcentage=20,
            date_debut=timezone.now().date(),
            date_fin=timezone.now().date() + timezone.timedelta(days=7),
            cree_par=self.visiteur_user
        )

    def test_admin_delete_rights_in_exploration(self):
        # 1. Visiteur normal ne peut pas supprimer
        self.client.force_login(self.visiteur_user)
        resp_lieu_visiteur = self.client.post(reverse('spots:spot_delete', args=[self.lieu.id]))
        self.assertTrue(Lieu.objects.filter(id=self.lieu.id).exists(), "Un visiteur ne peut pas supprimer un lieu tiers !")

        # 2. Admin se connecte et consulte Exploration
        self.client.force_login(self.admin_user)
        resp_explor = self.client.get(reverse('spots:spot_list'))
        self.assertEqual(resp_explor.status_code, 200)
        self.assertContains(resp_explor, "Supprimer")
        self.assertContains(resp_explor, reverse('spots:spot_delete', args=[self.lieu.id]))
        self.assertContains(resp_explor, reverse('events:event_delete', args=[self.event.id]))
        self.assertContains(resp_explor, reverse('events:offre_delete', args=[self.offre.id]))
        print("[OK] Page Exploration affiche les boutons de suppression pour l'Admin")

        # 3. Admin supprime le Lieu
        resp_del_lieu = self.client.post(reverse('spots:spot_delete', args=[self.lieu.id]), follow=True)
        self.assertEqual(resp_del_lieu.status_code, 200)
        self.assertFalse(Lieu.objects.filter(id=self.lieu.id).exists(), "L'admin doit pouvoir supprimer le lieu !")
        print("[OK] Suppression du lieu par Admin validée avec succès")

        # 4. Création d'un lieu pour tester la suppression d'un événement et d'une offre
        lieu2 = Lieu.objects.create(nom="Lieu 2", categorie=self.cat, quartier=self.quartier, adresse="Rue 2")
        ev2 = Evenement.objects.create(lieu=lieu2, titre="Event 2", description="Test", date_debut=timezone.now(), date_fin=timezone.now() + timezone.timedelta(hours=2))
        off2 = OffrePromotion.objects.create(lieu=lieu2, titre="Offre 2", description="Test", reduction_pourcentage=10, date_debut=timezone.now().date(), date_fin=timezone.now().date() + timezone.timedelta(days=5))

        resp_del_ev = self.client.post(reverse('events:event_delete', args=[ev2.id]), follow=True)
        self.assertEqual(resp_del_ev.status_code, 200)
        self.assertFalse(Evenement.objects.filter(id=ev2.id).exists(), "L'admin doit pouvoir supprimer l'événement !")
        print("[OK] Suppression de l'événement par Admin validée avec succès")

        resp_del_off = self.client.post(reverse('events:offre_delete', args=[off2.id]), follow=True)
        self.assertEqual(resp_del_off.status_code, 200)
        self.assertFalse(OffrePromotion.objects.filter(id=off2.id).exists(), "L'admin doit pouvoir supprimer l'offre !")
        print("[OK] Suppression de l'offre par Admin validée avec succès")

if __name__ == '__main__':
    import unittest
    unittest.main()
