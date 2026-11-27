import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunisspot.settings')
django.setup()

from django.test import Client
from users.models import Utilisateur
from spots.models import Lieu, Plat, Avis, Photo

client = Client()

print("--- 1. TEST RECHERCHE (Anonyme) ---")
res_search = client.get('/explorer/?q=Carthage')
assert res_search.status_code == 200
print("[OK] Recherche visiteur anonyme fonctionne (HTTP 200)")

print("\n--- 2. TEST FORMULAIRES AUTH & AUTOCOMPLETE ---")
res_login = client.get('/users/login/')
login_html = res_login.content.decode('utf-8')
assert 'autocomplete="off"' in login_html
print("[OK] Formulaire login possède autocomplete='off'")

res_register = client.get('/users/register/')
register_html = res_register.content.decode('utf-8')
assert 'autocomplete="off"' in register_html
assert 'autocomplete="new-password"' in register_html
print("[OK] Formulaire register possède autocomplete='off' et new-password")

print("\n--- 3. TEST ACCÈS AU MENU ---")
spot = Lieu.objects.first()
res_menu = client.get(f'/spot/{spot.slug}/menu/')
assert res_menu.status_code == 200
assert spot.nom in res_menu.content.decode('utf-8')
print(f"[OK] Page menu dédiée accessible pour {spot.nom} (HTTP 200)")

print("\n--- 4. TEST CRUD AVIS ---")
u_syrine = Utilisateur.objects.filter(username='syrine').first()
client.force_login(u_syrine)
res_add_avis = client.post(f'/spot/{spot.id}/avis/nouveau/', {
    'note': 5,
    'note_qualite': 5,
    'note_service': 5,
    'note_prix': 4,
    'note_ambiance': 5,
    'commentaire': 'Superbe expérience culinaire et cadre magnifique !'
}, follow=True)
assert res_add_avis.status_code == 200
nouvel_avis = Avis.objects.filter(user=u_syrine, lieu=spot).latest('date_publication')
print(f"[OK] Avis créé avec succès (ID: {nouvel_avis.id})")

# Edit avis by author
res_edit_avis = client.post(f'/avis/{nouvel_avis.id}/modifier/', {
    'note': 4,
    'note_qualite': 4,
    'note_service': 4,
    'note_prix': 4,
    'note_ambiance': 4,
    'commentaire': 'Modifié : Toujours très bon mais un peu d attente.'
}, follow=True)
assert res_edit_avis.status_code == 200
nouvel_avis.refresh_from_db()
assert nouvel_avis.note == 4
print("[OK] Modification de l'avis par son auteur validée")

# Attempt to edit avis by another normal user
u_amine = Utilisateur.objects.filter(username='amine').first()
client.force_login(u_amine)
res_hack_avis = client.get(f'/avis/{nouvel_avis.id}/modifier/')
# Direct GET without permission must return 302 redirect
assert res_hack_avis.status_code == 302
assert res_hack_avis.url == f'/spot/{spot.slug}/'
print("[OK] Sécurité permissions avis validée côté serveur (accès non-auteur redirigé 302)")

# Delete avis by author
client.force_login(u_syrine)
res_del_avis = client.post(f'/avis/{nouvel_avis.id}/supprimer/', follow=True)
assert res_del_avis.status_code == 200
assert not Avis.objects.filter(id=nouvel_avis.id).exists()
print("[OK] Suppression de l'avis par son auteur validée")

print("\n--- 5. TEST CRUD PHOTOS ---")
res_add_photo = client.post(f'/spot/{spot.id}/photos/nouvelle/', {
    'url': 'https://images.unsplash.com/photo-1544025162-d76694265947?w=800',
    'legende': 'Terrasse fleurie'
}, follow=True)
assert res_add_photo.status_code == 200
nouvelle_photo = Photo.objects.filter(user=u_syrine, lieu=spot).latest('date_ajout')
print(f"[OK] Photo ajoutée (ID: {nouvelle_photo.id})")

res_edit_photo = client.post(f'/photos/{nouvelle_photo.id}/modifier/', {
    'url': nouvelle_photo.url,
    'legende': 'Terrasse fleurie au coucher du soleil'
}, follow=True)
assert res_edit_photo.status_code == 200
nouvelle_photo.refresh_from_db()
assert nouvelle_photo.legende == 'Terrasse fleurie au coucher du soleil'
print("[OK] Photo modifiée par son auteur")

res_del_photo = client.post(f'/photos/{nouvelle_photo.id}/supprimer/', follow=True)
assert res_del_photo.status_code == 200
assert not Photo.objects.filter(id=nouvelle_photo.id).exists()
print("[OK] Photo supprimée avec succès")

print("\n--- 6. TEST ADMIN GESTION UTILISATEURS ---")
admin_user = Utilisateur.objects.filter(role='ADMIN').first()
client.force_login(admin_user)
res_admin_users = client.get('/dashboard/admin/utilisateurs/')
assert res_admin_users.status_code == 200
print("[OK] Liste des utilisateurs accessible par l'admin (HTTP 200)")

# Test delete user by admin
temp_user = Utilisateur.objects.filter(username='test_temp_user').first()
if not temp_user:
    temp_user = Utilisateur.objects.create_user(username='test_temp_user', email='temp@tunisspot.tn', password='password123')

res_del_user = client.post(f'/dashboard/admin/utilisateurs/{temp_user.id}/supprimer/', follow=True)
assert res_del_user.status_code == 200
assert not Utilisateur.objects.filter(id=temp_user.id).exists()
print("[OK] Suppression d'utilisateur par l'admin validée avec succès")

# Prevent admin from deleting self
res_del_self = client.get(f'/dashboard/admin/utilisateurs/{admin_user.id}/supprimer/')
assert res_del_self.status_code == 302
assert res_del_self.url == '/dashboard/admin/utilisateurs/'
print("[OK] Sécurité anti auto-suppression admin validée (Redirection 302)")

print("\n========================================================")
print("=== TOUS LES TESTS VALIDÉS AVEC SUCCÈS À 100% ===")
print("========================================================")
