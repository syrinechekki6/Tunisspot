"""
Test complet de vérification de la synchronisation temps réel des CRUD avec Oracle XE
"""
import os
import django
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunisspot.settings')
django.setup()

from django.test import Client
from users.models import Utilisateur
from spots.models import Lieu, Plat, Avis
from events.models import Evenement, OffrePromotion

def run_oracle_query(sql):
    cmd = f"""
SET DEFINE OFF;
SET FEEDBACK OFF;
ALTER SESSION SET CURRENT_SCHEMA = TUNISSPOT_SOFT;
{sql}
EXIT;
"""
    proc = subprocess.run(
        [r"C:\oraclexe\app\oracle\product\11.2.0\server\bin\sqlplus.exe", "-S", "/", "as", "sysdba"],
        input=cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )
    return proc.stdout.strip()

def test_full_crud_realtime_sync():
    print("=== DÉBUT DU TEST CRUD TEMPS RÉEL AVEC ORACLE ===")
    c = Client()

    # 1. TEST INSCRIPTION D'UN NOUVEL UTILISATEUR
    print("\n1. Test création nouvel utilisateur (Inscription)...")
    username_test = "test_crud_oracle"
    Utilisateur.objects.filter(username=username_test).delete()

    resp = c.post('/users/register/', {
        'username': username_test,
        'nom': 'Utilisateur Test Oracle',
        'email': 'oracle_test@tunisspot.tn',
        'role': 'TOURISTE',
        'langue': 'FR',
        'password1': 'Azerty1234!',
        'password2': 'Azerty1234!',
    }, follow=True)

    user_obj = Utilisateur.objects.filter(username=username_test).first()
    assert user_obj is not None, "L'utilisateur doit être créé dans Django/SQLite !"
    print(f"   [SQLite] Utilisateur créé avec succès : ID={user_obj.id}, username={user_obj.username}")

    # Vérification Oracle
    oracle_check = run_oracle_query(f"SELECT username, email FROM UTILISATEUR WHERE ID = {user_obj.id};")
    print(f"   [Oracle] Résultat requête Oracle :\n{oracle_check}")
    assert username_test in oracle_check, f"{username_test} doit être présent dans Oracle UTILISATEUR !"

    # 2. TEST MODIFICATION UTILISATEUR
    print("\n2. Test modification utilisateur...")
    user_obj.nom = "Nom Modifié Test"
    user_obj.points = 120
    user_obj.save()

    oracle_check = run_oracle_query(f"SELECT nom, points FROM UTILISATEUR WHERE ID = {user_obj.id};")
    print(f"   [Oracle] Résultat requête Oracle après modification :\n{oracle_check}")
    assert "Nom Modifi" in oracle_check or "120" in oracle_check, "Modification doit être répercutée dans Oracle !"

    # 3. TEST CRUD PLAT (MENU)
    print("\n3. Test création, modification et suppression Plat...")
    lieu = Lieu.objects.first()
    plat = Plat.objects.create(
        lieu=lieu,
        nom="Plat Test Sync Oracle",
        description="Délicieux plat test",
        prix=18.5,
        categorie_plat="Plat principal"
    )
    oracle_plat = run_oracle_query(f"SELECT nom, prix FROM PLAT WHERE ID = {plat.id};")
    print(f"   [Oracle] Plat créé dans Oracle :\n{oracle_plat}")
    assert "Plat Test Sync Oracle" in oracle_plat, "Le plat doit être dans Oracle PLAT !"

    # Modification Plat
    plat.prix = 22.0
    plat.nom = "Plat Test Sync Modifié"
    plat.save()
    oracle_plat_mod = run_oracle_query(f"SELECT nom, prix FROM PLAT WHERE ID = {plat.id};")
    print(f"   [Oracle] Plat modifié dans Oracle :\n{oracle_plat_mod}")
    assert "22" in oracle_plat_mod, "Le prix modifié doit être dans Oracle !"

    # Suppression Plat
    plat_id = plat.id
    plat.delete()
    oracle_plat_del = run_oracle_query(f"SELECT count(*) FROM PLAT WHERE ID = {plat_id};")
    print(f"   [Oracle] Plat supprimé dans Oracle (count) : {oracle_plat_del}")
    assert "0" in oracle_plat_del, "Le plat doit être supprimé d'Oracle !"

    # 4. TEST SUPPRESSION UTILISATEUR (ADMIN DELETE)
    print("\n4. Test suppression utilisateur...")
    user_id = user_obj.id
    user_obj.delete()

    oracle_user_del = run_oracle_query(f"SELECT count(*) FROM UTILISATEUR WHERE ID = {user_id};")
    print(f"   [Oracle] Utilisateur supprimé dans Oracle (count) : {oracle_user_del}")
    assert "0" in oracle_user_del, "L'utilisateur doit être supprimé d'Oracle !"

    print("\n=== TOUS LES TESTS CRUD TEMPS RÉEL ORACLE SONT PASSÉS À 100% AVEC SUCCÈS ! ===")

if __name__ == '__main__':
    test_full_crud_realtime_sync()
