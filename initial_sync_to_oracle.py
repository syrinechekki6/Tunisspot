"""
Script de synchronisation complète de SQLite vers Oracle XE (TUNISSPOT_SOFT)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunisspot.settings')
django.setup()

from users.models import Utilisateur, Preference
from spots.models import Categorie, Quartier, Lieu, Plat, Avis, Photo
from events.models import Evenement, OffrePromotion
import oracle_sync

def sync_all():
    print("=== DÉBUT DE LA SYNCHRONISATION SQLITE -> ORACLE XE ===")

    # 1. CATEGORIES
    print("1. Synchronisation des catégories...")
    cats = Categorie.objects.all()
    cat_stmts = []
    for c in cats:
        lib = oracle_sync.sql_str(c.libelle)
        slug = oracle_sync.sql_str(c.slug)
        icon = oracle_sync.sql_str(c.icone or 'utensils')
        img = oracle_sync.sql_str(c.image_couverture or '')
        desc = oracle_sync.sql_str(c.description or '')
        cat_stmts.append(f"""
MERGE INTO CATEGORIE d USING (SELECT {c.id} AS ID FROM DUAL) s ON (d.ID = s.ID)
WHEN MATCHED THEN UPDATE SET LIBELLE = {lib}, SLUG = {slug}, ICONE = {icon}, IMAGE_COUVERTURE = {img}, DESCRIPTION = {desc}
WHEN NOT MATCHED THEN INSERT (ID, LIBELLE, SLUG, ICONE, IMAGE_COUVERTURE, DESCRIPTION) VALUES ({c.id}, {lib}, {slug}, {icon}, {img}, {desc});
""")
    oracle_sync.run_oracle_commands("\n".join(cat_stmts))
    print(f"   -> {len(cats)} catégories synchronisées.")

    # 2. QUARTIERS
    print("2. Synchronisation des quartiers...")
    quarts = Quartier.objects.all()
    q_stmts = []
    for q in quarts:
        nom = oracle_sync.sql_str(q.nom)
        ville = oracle_sync.sql_str(q.ville or 'Tunis')
        lat = oracle_sync.sql_num(q.latitude, "36.8065")
        lng = oracle_sync.sql_num(q.longitude, "10.1815")
        img = oracle_sync.sql_str(q.image_url or '')
        desc = oracle_sync.sql_str(q.description or '')
        q_stmts.append(f"""
MERGE INTO QUARTIER d USING (SELECT {q.id} AS ID FROM DUAL) s ON (d.ID = s.ID)
WHEN MATCHED THEN UPDATE SET NOM = {nom}, VILLE = {ville}, LATITUDE = {lat}, LONGITUDE = {lng}, IMAGE_URL = {img}, DESCRIPTION = {desc}
WHEN NOT MATCHED THEN INSERT (ID, NOM, VILLE, LATITUDE, LONGITUDE, IMAGE_URL, DESCRIPTION) VALUES ({q.id}, {nom}, {ville}, {lat}, {lng}, {img}, {desc});
""")
    oracle_sync.run_oracle_commands("\n".join(q_stmts))
    print(f"   -> {len(quarts)} quartiers synchronisés.")

    # 3. UTILISATEURS
    print("3. Synchronisation des utilisateurs...")
    users = Utilisateur.objects.all()
    for u in users:
        oracle_sync.sync_oracle_utilisateur(u)
    print(f"   -> {len(users)} utilisateurs synchronisés dans UTILISATEUR.")

    # 4. LIEUX
    print("4. Synchronisation des lieux (spots)...")
    lieux = Lieu.objects.all()
    for l in lieux:
        oracle_sync.sync_oracle_lieu(l)
    print(f"   -> {len(lieux)} lieux synchronisés dans LIEU.")

    # 5. PLATS
    print("5. Synchronisation des plats...")
    plats = Plat.objects.all()
    for p in plats:
        oracle_sync.sync_oracle_plat(p)
    print(f"   -> {len(plats)} plats synchronisés dans PLAT.")

    # 6. AVIS
    print("6. Synchronisation des avis...")
    avis_list = Avis.objects.all()
    for a in avis_list:
        oracle_sync.sync_oracle_avis(a)
    print(f"   -> {len(avis_list)} avis synchronisés dans AVIS.")

    # 7. PHOTOS
    print("7. Synchronisation des photos...")
    photos = Photo.objects.all()
    for ph in photos:
        oracle_sync.sync_oracle_photo(ph)
    print(f"   -> {len(photos)} photos synchronisées dans PHOTO.")

    # 8. EVENEMENTS
    print("8. Synchronisation des événements...")
    events = Evenement.objects.all()
    for ev in events:
        oracle_sync.sync_oracle_evenement(ev)
    print(f"   -> {len(events)} événements synchronisés dans EVENEMENT.")

    # 9. OFFRES PROMOTION
    print("9. Synchronisation des offres promotions...")
    offres = OffrePromotion.objects.all()
    for of in offres:
        oracle_sync.sync_oracle_offre(of)
    print(f"   -> {len(offres)} offres synchronisées dans OFFRE_PROMOTION.")

    print("=== SYNCHRONISATION COMPLÈTE TERMINÉE AVEC SUCCÈS ! ===")

if __name__ == '__main__':
    sync_all()
