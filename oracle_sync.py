"""
Synchroniseur Automatique Temps-Réel SQLite <-> Oracle (Software_Tunisspot)
Permet à chaque opération CRUD (Création, Modification, Suppression) dans l'application web
d'être immédiatement reflétée dans la base de données Oracle XE (schéma TUNISSPOT_SOFT).
"""

import os
import subprocess
import datetime
import logging

logger = logging.getLogger(__name__)

SQLPLUS_PATH = r"C:\oraclexe\app\oracle\product\11.2.0\server\bin\sqlplus.exe"

def esc(val):
    if val is None:
        return ""
    return str(val).replace("'", "''")

def sql_str(val):
    if val is None:
        return "NULL"
    return f"'{esc(val)}'"

def sql_num(val, default="0"):
    if val is None:
        return default
    return str(val)

def run_oracle_commands(sql_statements):
    """Exécute une suite de commandes SQL dans Oracle XE via SQL*Plus"""
    if not os.path.exists(SQLPLUS_PATH):
        return False, "sqlplus.exe introuvable"

    # Encapsulation dans les schémas TUNISSPOT_SOFT et TUNISSPOT pour SQL Developer
    combined_sql = f"""
SET DEFINE OFF;
SET FEEDBACK OFF;
WHENEVER SQLERROR CONTINUE;
ALTER SESSION SET CURRENT_SCHEMA = TUNISSPOT_SOFT;
{sql_statements}
COMMIT;
ALTER SESSION SET CURRENT_SCHEMA = TUNISSPOT;
{sql_statements}
COMMIT;
EXIT;
"""

    try:
        proc = subprocess.run(
            [SQLPLUS_PATH, "-S", "/", "as", "sysdba"],
            input=combined_sql,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=10
        )
        return True, proc.stdout
    except Exception as e:
        logger.debug(f"Info sync Oracle: {e}")
        return False, str(e)


# ==============================================================================
# SYNCHRONISATION UTILISATEUR
# ==============================================================================
def sync_oracle_utilisateur(instance, deleted=False):
    if deleted:
        sql = f"""
DELETE FROM UTILISATEUR WHERE ID = {instance.id};
"""
    else:
        nom = sql_str(instance.nom or instance.username)
        username = sql_str(instance.username)
        email = sql_str(instance.email or f"{instance.username}@tunisspot.tn")
        mdp = sql_str(instance.password or 'pbkdf2_sha256$default')
        langue = sql_str(instance.langue or 'FR')
        role = sql_str(instance.role or 'TOURISTE')
        tel = sql_str(instance.telephone or '')
        avatar = sql_str(instance.avatar_url or '')
        pts = sql_num(instance.points, "50")
        conf = sql_num(instance.niveau_confiance, "1.0")
        guide = "1" if instance.est_guide_local else "0"

        sql = f"""
MERGE INTO UTILISATEUR d
USING (SELECT {instance.id} AS ID FROM DUAL) s
ON (d.ID = s.ID)
WHEN MATCHED THEN
  UPDATE SET USERNAME = {username}, NOM = {nom}, EMAIL = {email}, MOT_DE_PASSE = {mdp},
             LANGUE = {langue}, ROLE = {role}, TELEPHONE = {tel}, AVATAR_URL = {avatar},
             POINTS = {pts}, SCORE_CONFIANCE = {conf}, EST_GUIDE_LOCAL = {guide}
WHEN NOT MATCHED THEN
  INSERT (ID, USERNAME, NOM, EMAIL, MOT_DE_PASSE, LANGUE, ROLE, TELEPHONE, AVATAR_URL, POINTS, SCORE_CONFIANCE, EST_GUIDE_LOCAL, DATE_INSCRIPTION)
  VALUES ({instance.id}, {username}, {nom}, {email}, {mdp}, {langue}, {role}, {tel}, {avatar}, {pts}, {conf}, {guide}, CURRENT_TIMESTAMP);
"""
    run_oracle_commands(sql)


# ==============================================================================
# SYNCHRONISATION LIEU (SPOT)
# ==============================================================================
def sync_oracle_lieu(instance, deleted=False):
    if deleted:
        sql = f"DELETE FROM LIEU WHERE ID = {instance.id};"
    else:
        nom = sql_str(instance.nom)
        slug = sql_str(instance.slug)
        place_id = sql_str(instance.place_id or f"spot_{instance.id}")
        cat_id = sql_num(instance.categorie_id)
        quart_id = sql_num(instance.quartier_id, "NULL")
        adresse = sql_str(instance.adresse)
        lat = sql_num(instance.latitude, "36.8065")
        lng = sql_num(instance.longitude, "10.1815")
        tel = sql_str(instance.telephone or "")
        web = sql_str(instance.site_web or "")
        prix_fourch = sql_str(instance.fourchette_prix or "€€")
        prix_moy = sql_num(instance.prix_moyen, "25.0")
        horaires = sql_str(instance.horaires or "Tous les jours 08:00 - 23:00")
        desc = sql_str(instance.description or "")
        img = sql_str(instance.image_principale or "")
        note = sql_num(instance.note_moyenne, "4.5")
        nb_avis = sql_num(instance.nombre_avis, "0")
        pepite = "1" if instance.est_pepite_locale else "0"
        foule = sql_str(instance.indice_foule or "Moyen")
        statut = sql_str(instance.statut or "ACTIF")
        proprio = sql_num(instance.proprietaire_id, "NULL")

        wifi = "1" if instance.wifi else "0"
        terrasse = "1" if instance.terrasse else "0"
        parking = "1" if instance.parking else "0"
        pmr = "1" if instance.acces_pmr else "0"
        vue_mer = "1" if instance.vue_mer else "0"
        clim = "1" if instance.climatisation else "0"
        romantique = "1" if instance.ambiance_romantique else "0"
        famille = "1" if instance.ambiance_famille else "0"
        amis = "1" if instance.ambiance_amis else "0"
        halal = "1" if instance.halal else "0"
        vege = "1" if instance.vegetarien else "0"

        sql = f"""
MERGE INTO LIEU d
USING (SELECT {instance.id} AS ID FROM DUAL) s
ON (d.ID = s.ID)
WHEN MATCHED THEN
  UPDATE SET NOM = {nom}, SLUG = {slug}, PLACE_ID = {place_id}, CATEGORIE_ID = {cat_id}, QUARTIER_ID = {quart_id},
             ADRESSE = {adresse}, LATITUDE = {lat}, LONGITUDE = {lng}, TELEPHONE = {tel}, SITE_WEB = {web},
             FOURCHETTE_PRIX = {prix_fourch}, PRIX_MOYEN = {prix_moy}, HORAIRES = {horaires}, DESCRIPTION = {desc},
             IMAGE_PRINCIPALE = {img}, NOTE_MOYENNE = {note}, NOMBRE_AVIS = {nb_avis}, EST_PEPITE_LOCALE = {pepite},
             INDICE_FOULE = {foule}, STATUT = {statut}, PROPRIETAIRE_ID = {proprio},
             WIFI = {wifi}, TERRASSE = {terrasse}, PARKING = {parking}, ACCES_PMR = {pmr}, VUE_MER = {vue_mer},
             CLIMATISATION = {clim}, AMBIANCE_ROMANTIQUE = {romantique}, AMBIANCE_FAMILLE = {famille},
             AMBIANCE_AMIS = {amis}, HALAL = {halal}, VEGETARIEN = {vege}
WHEN NOT MATCHED THEN
  INSERT (ID, PLACE_ID, NOM, SLUG, CATEGORIE_ID, QUARTIER_ID, ADRESSE, LATITUDE, LONGITUDE, TELEPHONE, SITE_WEB,
          FOURCHETTE_PRIX, PRIX_MOYEN, HORAIRES, DESCRIPTION, IMAGE_PRINCIPALE, NOTE_MOYENNE, NOMBRE_AVIS,
          EST_PEPITE_LOCALE, INDICE_FOULE, STATUT, WIFI, TERRASSE, PARKING, ACCES_PMR, VUE_MER, CLIMATISATION,
          AMBIANCE_ROMANTIQUE, AMBIANCE_FAMILLE, AMBIANCE_AMIS, HALAL, VEGETARIEN, PROPRIETAIRE_ID, DATE_CREATION)
  VALUES ({instance.id}, {place_id}, {nom}, {slug}, {cat_id}, {quart_id}, {adresse}, {lat}, {lng}, {tel}, {web},
          {prix_fourch}, {prix_moy}, {horaires}, {desc}, {img}, {note}, {nb_avis},
          {pepite}, {foule}, {statut}, {wifi}, {terrasse}, {parking}, {pmr}, {vue_mer}, {clim},
          {romantique}, {famille}, {amis}, {halal}, {vege}, {proprio}, CURRENT_TIMESTAMP);
"""
    run_oracle_commands(sql)


# ==============================================================================
# SYNCHRONISATION PLAT (MENU)
# ==============================================================================
def sync_oracle_plat(instance, deleted=False):
    if deleted:
        sql = f"DELETE FROM PLAT WHERE ID = {instance.id};"
    else:
        lieu_id = sql_num(instance.lieu_id)
        nom = sql_str(instance.nom)
        desc = sql_str(instance.description or "")
        prix = sql_num(instance.prix, "10.0")
        cat = sql_str(instance.categorie_plat or "Plat principal")
        photo = sql_str(instance.photo or "")
        pop = "1" if instance.est_populaire else "0"

        sql = f"""
MERGE INTO PLAT d
USING (SELECT {instance.id} AS ID FROM DUAL) s
ON (d.ID = s.ID)
WHEN MATCHED THEN
  UPDATE SET LIEU_ID = {lieu_id}, NOM = {nom}, DESCRIPTION = {desc}, PRIX = {prix},
             CATEGORIE_PLAT = {cat}, PHOTO = {photo}, EST_POPULAIRE = {pop}
WHEN NOT MATCHED THEN
  INSERT (ID, LIEU_ID, NOM, DESCRIPTION, PRIX, CATEGORIE_PLAT, PHOTO, EST_POPULAIRE)
  VALUES ({instance.id}, {lieu_id}, {nom}, {desc}, {prix}, {cat}, {photo}, {pop});
"""
    run_oracle_commands(sql)


# ==============================================================================
# SYNCHRONISATION AVIS
# ==============================================================================
def sync_oracle_avis(instance, deleted=False):
    if deleted:
        sql = f"DELETE FROM AVIS WHERE ID = {instance.id};"
    else:
        lieu_id = sql_num(instance.lieu_id)
        user_id = sql_num(instance.user_id)
        note = sql_num(instance.note, "5")
        q = sql_num(instance.note_qualite, "5")
        s = sql_num(instance.note_service, "5")
        p = sql_num(instance.note_prix, "5")
        a = sql_num(instance.note_ambiance, "5")
        comm = sql_str(instance.commentaire)
        stat = sql_str(instance.statut_moderation or "APPROUVE")
        sign = sql_num(instance.nombre_signalements, "0")
        conf = sql_num(instance.score_confiance, "1.0")
        typ = sql_str(instance.type_visiteur or "RESIDENT")

        sql = f"""
MERGE INTO AVIS d
USING (SELECT {instance.id} AS ID FROM DUAL) s
ON (d.ID = s.ID)
WHEN MATCHED THEN
  UPDATE SET LIEU_ID = {lieu_id}, UTILISATEUR_ID = {user_id}, NOTE = {note},
             NOTE_QUALITE = {q}, NOTE_SERVICE = {s}, NOTE_PRIX = {p}, NOTE_AMBIANCE = {a},
             COMMENTAIRE = {comm}, STATUT_MODERATION = {stat}, NOMBRE_SIGNALEMENTS = {sign},
             SCORE_CONFIANCE = {conf}, TYPE_VISITEUR = {typ}
WHEN NOT MATCHED THEN
  INSERT (ID, LIEU_ID, UTILISATEUR_ID, NOTE, NOTE_QUALITE, NOTE_SERVICE, NOTE_PRIX, NOTE_AMBIANCE,
          COMMENTAIRE, STATUT_MODERATION, NOMBRE_SIGNALEMENTS, SCORE_CONFIANCE, TYPE_VISITEUR, DATE_PUBLICATION)
  VALUES ({instance.id}, {lieu_id}, {user_id}, {note}, {q}, {s}, {p}, {a},
          {comm}, {stat}, {sign}, {conf}, {typ}, CURRENT_TIMESTAMP);
"""
    run_oracle_commands(sql)


# ==============================================================================
# SYNCHRONISATION PHOTO
# ==============================================================================
def sync_oracle_photo(instance, deleted=False):
    if deleted:
        sql = f"DELETE FROM PHOTO WHERE ID = {instance.id};"
    else:
        lieu_id = sql_num(instance.lieu_id)
        user_id = sql_num(instance.user_id, "NULL")
        url = sql_str(instance.image_url or instance.url)
        legende = sql_str(instance.legende or "")
        source = sql_str(instance.source or "COMMUNAUTE")
        stat = sql_str(instance.statut_moderation or "APPROUVE")

        sql = f"""
MERGE INTO PHOTO d
USING (SELECT {instance.id} AS ID FROM DUAL) s
ON (d.ID = s.ID)
WHEN MATCHED THEN
  UPDATE SET LIEU_ID = {lieu_id}, UTILISATEUR_ID = {user_id}, URL = {url},
             LEGENDE = {legende}, SOURCE = {source}, STATUT_MODERATION = {stat}
WHEN NOT MATCHED THEN
  INSERT (ID, LIEU_ID, UTILISATEUR_ID, URL, LEGENDE, SOURCE, STATUT_MODERATION, DATE_AJOUT)
  VALUES ({instance.id}, {lieu_id}, {user_id}, {url}, {legende}, {source}, {stat}, CURRENT_TIMESTAMP);
"""
    run_oracle_commands(sql)


# ==============================================================================
# SYNCHRONISATION ÉVÉNEMENT & OFFRE PROMOTION
# ==============================================================================
def sync_oracle_evenement(instance, deleted=False):
    if deleted:
        sql = f"DELETE FROM EVENEMENT WHERE ID = {instance.id};"
    else:
        lieu_id = sql_num(instance.lieu_id)
        titre = sql_str(instance.titre)
        desc = sql_str(instance.description or "")
        img = sql_str(instance.image or "")
        prix = sql_num(instance.prix, "0.0")
        cat = sql_str(instance.categorie or "Autre")
        pop = "1" if instance.est_populaire else "0"

        sql = f"""
MERGE INTO EVENEMENT d
USING (SELECT {instance.id} AS ID FROM DUAL) s
ON (d.ID = s.ID)
WHEN MATCHED THEN
  UPDATE SET LIEU_ID = {lieu_id}, TITRE = {titre}, DESCRIPTION = {desc},
             IMAGE = {img}, PRIX = {prix}, CATEGORIE = {cat}, EST_POPULAIRE = {pop}
WHEN NOT MATCHED THEN
  INSERT (ID, LIEU_ID, TITRE, DESCRIPTION, IMAGE, PRIX, CATEGORIE, EST_POPULAIRE, DATE_DEBUT, DATE_FIN)
  VALUES ({instance.id}, {lieu_id}, {titre}, {desc}, {img}, {prix}, {cat}, {pop}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + 7);
"""
    run_oracle_commands(sql)


def sync_oracle_offre(instance, deleted=False):
    if deleted:
        sql = f"DELETE FROM OFFRE_PROMOTION WHERE ID = {instance.id};"
    else:
        lieu_id = sql_num(instance.lieu_id)
        titre = sql_str(instance.titre)
        desc = sql_str(instance.description or "")
        reduc = sql_num(getattr(instance, 'reduction_pourcentage', 15), "15")
        code = sql_str(instance.code_promo or "")
        active = "1" if instance.est_active else "0"

        sql = f"""
MERGE INTO OFFRE_PROMOTION d
USING (SELECT {instance.id} AS ID FROM DUAL) s
ON (d.ID = s.ID)
WHEN MATCHED THEN
  UPDATE SET LIEU_ID = {lieu_id}, TITRE = {titre}, DESCRIPTION = {desc},
             REDUCTION_POURCENTAGE = {reduc}, CODE_PROMO = {code}, EST_ACTIVE = {active}
WHEN NOT MATCHED THEN
  INSERT (ID, LIEU_ID, TITRE, DESCRIPTION, REDUCTION_POURCENTAGE, CODE_PROMO, EST_ACTIVE, DATE_DEBUT, DATE_FIN)
  VALUES ({instance.id}, {lieu_id}, {titre}, {desc}, {reduc}, {code}, {active}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + 30);
"""
    run_oracle_commands(sql)


# ==============================================================================
# ENREGISTREMENT DES SIGNAUX DJANGO
# ==============================================================================
_signals_registered = False

def register_oracle_sync_signals():
    global _signals_registered
    if _signals_registered:
        return
    _signals_registered = True

    from django.db.models.signals import post_save, post_delete
    from users.models import Utilisateur
    from spots.models import Lieu, Plat, Avis, Photo
    from events.models import Evenement, OffrePromotion

    def on_user_save(sender, instance, **kwargs):
        try: sync_oracle_utilisateur(instance, deleted=False)
        except Exception: pass

    def on_user_delete(sender, instance, **kwargs):
        try: sync_oracle_utilisateur(instance, deleted=True)
        except Exception: pass

    def on_lieu_save(sender, instance, **kwargs):
        try: sync_oracle_lieu(instance, deleted=False)
        except Exception: pass

    def on_lieu_delete(sender, instance, **kwargs):
        try: sync_oracle_lieu(instance, deleted=True)
        except Exception: pass

    def on_plat_save(sender, instance, **kwargs):
        try: sync_oracle_plat(instance, deleted=False)
        except Exception: pass

    def on_plat_delete(sender, instance, **kwargs):
        try: sync_oracle_plat(instance, deleted=True)
        except Exception: pass

    def on_avis_save(sender, instance, **kwargs):
        try: sync_oracle_avis(instance, deleted=False)
        except Exception: pass

    def on_avis_delete(sender, instance, **kwargs):
        try: sync_oracle_avis(instance, deleted=True)
        except Exception: pass

    def on_photo_save(sender, instance, **kwargs):
        try: sync_oracle_photo(instance, deleted=False)
        except Exception: pass

    def on_photo_delete(sender, instance, **kwargs):
        try: sync_oracle_photo(instance, deleted=True)
        except Exception: pass

    def on_event_save(sender, instance, **kwargs):
        try: sync_oracle_evenement(instance, deleted=False)
        except Exception: pass

    def on_event_delete(sender, instance, **kwargs):
        try: sync_oracle_evenement(instance, deleted=True)
        except Exception: pass

    def on_offre_save(sender, instance, **kwargs):
        try: sync_oracle_offre(instance, deleted=False)
        except Exception: pass

    def on_offre_delete(sender, instance, **kwargs):
        try: sync_oracle_offre(instance, deleted=True)
        except Exception: pass

    post_save.connect(on_user_save, sender=Utilisateur, weak=False)
    post_delete.connect(on_user_delete, sender=Utilisateur, weak=False)

    post_save.connect(on_lieu_save, sender=Lieu, weak=False)
    post_delete.connect(on_lieu_delete, sender=Lieu, weak=False)

    post_save.connect(on_plat_save, sender=Plat, weak=False)
    post_delete.connect(on_plat_delete, sender=Plat, weak=False)

    post_save.connect(on_avis_save, sender=Avis, weak=False)
    post_delete.connect(on_avis_delete, sender=Avis, weak=False)

    post_save.connect(on_photo_save, sender=Photo, weak=False)
    post_delete.connect(on_photo_delete, sender=Photo, weak=False)

    post_save.connect(on_event_save, sender=Evenement, weak=False)
    post_delete.connect(on_event_delete, sender=Evenement, weak=False)

    post_save.connect(on_offre_save, sender=OffrePromotion, weak=False)
    post_delete.connect(on_offre_delete, sender=OffrePromotion, weak=False)

    logger.info("Signaux de synchronisation automatique Oracle enregistrés avec succès.")
