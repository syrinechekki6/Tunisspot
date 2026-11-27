import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Initialise ou réinitialise le compte Administrateur par défaut sécurisé (Seed / Identifiants via variables d'environnement)"

    def handle(self, *args, **options):
        # Récupération sécurisée depuis les variables d'environnement (avec valeurs par défaut saines)
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@tunisspot.tn')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'AdminTunisSpot2026!')
        admin_nom = os.environ.get('ADMIN_NOM', 'Administrateur Général')

        user, created = User.objects.get_or_create(username=admin_username, defaults={'email': admin_email})
        user.email = admin_email
        user.nom = admin_nom
        user.role = 'ADMIN'
        user.is_staff = True
        user.is_superuser = True
        user.set_password(admin_password)  # Hash sécurisé automatique (PBKDF2/SHA256)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Compte Admin créé avec succès : '{admin_username}' ({admin_email})"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Compte Admin mis à jour et sécurisé : '{admin_username}' ({admin_email})"))
