-- =====================================================================
-- APPLICATION : TUNISSPOT - GUIDE DE SORTIES ET BONS PLANS À TUNIS
-- SCRIPT DE BASE DE DONNÉES CONFORME À 100% AU DIAGRAMME DE CLASSES UML
-- Compatible : Oracle Database (11g XE, 12c, 19c, 21c, 23c), SQL Developer
-- =====================================================================

SET DEFINE OFF;

-- =====================================================================
-- 0. NETTOYAGE PRÉALABLE DES TABLES ET SÉQUENCES
-- =====================================================================
BEGIN
   FOR c IN (SELECT table_name FROM user_tables WHERE table_name IN (
       'PREFERENCE', 'NOTIFICATION', 'ETAPE', 'ITINERAIRE', 
       'FAVORIS_LIEUX', 'LISTE_FAVORIS', 'AVIS', 'PHOTO', 
       'PLAT', 'EVENEMENT', 'LIEU_STATION', 'STATION', 
       'LIEU', 'CATEGORIE', 'UTILISATEUR'
   )) LOOP
      BEGIN
         EXECUTE IMMEDIATE 'DROP TABLE "' || c.table_name || '" CASCADE CONSTRAINTS';
      EXCEPTION WHEN OTHERS THEN NULL;
      END;
   END LOOP;

   FOR s IN (SELECT sequence_name FROM user_sequences WHERE sequence_name IN (
       'SEQ_PREFERENCE', 'SEQ_NOTIFICATION', 'SEQ_ETAPE', 'SEQ_ITINERAIRE',
       'SEQ_LISTE_FAVORIS', 'SEQ_AVIS', 'SEQ_PHOTO', 'SEQ_PLAT',
       'SEQ_EVENEMENT', 'SEQ_STATION', 'SEQ_LIEU', 'SEQ_CATEGORIE', 'SEQ_UTILISATEUR'
   )) LOOP
      BEGIN
         EXECUTE IMMEDIATE 'DROP SEQUENCE "' || s.sequence_name || '"';
      EXCEPTION WHEN OTHERS THEN NULL;
      END;
   END LOOP;
END;
/

-- =====================================================================
-- 1. TABLE UTILISATEUR
-- Diagramme : Utilisateur (id, nom, email, motDePasse, langue, role, dateInscription)
-- Méthodes : +sInscrire(), +seConnecter(), +signalerAvis()
-- =====================================================================
CREATE SEQUENCE SEQ_UTILISATEUR START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE TABLE UTILISATEUR (
    ID NUMBER PRIMARY KEY,
    NOM VARCHAR2(150) NOT NULL,
    EMAIL VARCHAR2(150) NOT NULL UNIQUE,
    MOT_DE_PASSE VARCHAR2(255) NOT NULL,
    LANGUE VARCHAR2(20) DEFAULT 'FR',
    ROLE VARCHAR2(30) DEFAULT 'VISITEUR', -- 'VISITEUR', 'PROPRIETAIRE', 'ADMIN'
    DATE_INSCRIPTION TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE OR REPLACE TRIGGER TRG_UTILISATEUR
BEFORE INSERT ON UTILISATEUR FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_UTILISATEUR.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- =====================================================================
-- 2. TABLE PREFERENCE
-- Diagramme : Preference (id, budgetMax, ambiances, regimes)
-- Relation  : Utilisateur (1) -- définit --> (1) Preference
-- Méthodes  : +enregistrer()
-- =====================================================================
CREATE SEQUENCE SEQ_PREFERENCE START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE TABLE PREFERENCE (
    ID NUMBER PRIMARY KEY,
    UTILISATEUR_ID NUMBER NOT NULL UNIQUE,
    BUDGET_MAX NUMBER(8,2) DEFAULT 100.0,
    AMBIANCES VARCHAR2(255) DEFAULT 'calme,terrasse,romantique',
    REGIMES VARCHAR2(255) DEFAULT 'halal',
    CONSTRAINT FK_PREF_UTILISATEUR FOREIGN KEY (UTILISATEUR_ID) REFERENCES UTILISATEUR(ID) ON DELETE CASCADE
);

CREATE OR REPLACE TRIGGER TRG_PREFERENCE
BEFORE INSERT ON PREFERENCE FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_PREFERENCE.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- =====================================================================
-- 3. TABLE NOTIFICATION
-- Diagramme : Notification (id, titre, message, dateEnvoi, estLue)
-- Relation  : Utilisateur (1) -- reçoit --> (0..*) Notification
-- Méthodes  : +envoyer(), +marquerCommeLue()
-- =====================================================================
CREATE SEQUENCE SEQ_NOTIFICATION START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE TABLE NOTIFICATION (
    ID NUMBER PRIMARY KEY,
    UTILISATEUR_ID NUMBER NOT NULL,
    TITRE VARCHAR2(200) NOT NULL,
    MESSAGE VARCHAR2(1000) NOT NULL,
    DATE_ENVOI TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    EST_LUE NUMBER(1) DEFAULT 0, -- 0 = non lue, 1 = lue
    CONSTRAINT FK_NOTIF_UTILISATEUR FOREIGN KEY (UTILISATEUR_ID) REFERENCES UTILISATEUR(ID) ON DELETE CASCADE
);

CREATE OR REPLACE TRIGGER TRG_NOTIFICATION
BEFORE INSERT ON NOTIFICATION FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_NOTIFICATION.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- =====================================================================
-- 4. TABLE CATEGORIE
-- Diagramme : Categorie (id, libelle, icone)
-- Relation  : Categorie (1) <-- appartient à -- (0..*) Lieu
-- =====================================================================
CREATE SEQUENCE SEQ_CATEGORIE START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE TABLE CATEGORIE (
    ID NUMBER PRIMARY KEY,
    LIBELLE VARCHAR2(100) NOT NULL UNIQUE,
    ICONE VARCHAR2(100) DEFAULT 'fa-utensils'
);

CREATE OR REPLACE TRIGGER TRG_CATEGORIE
BEFORE INSERT ON CATEGORIE FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_CATEGORIE.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- =====================================================================
-- 5. TABLE LIEU
-- Diagramme : Lieu (id, placeId, nom, adresse, latitude, longitude,
--             telephone, siteWeb, fourchettePrix, horaires, noteMoyenne, statut)
-- Méthodes  : +rechercher(), +calculerNoteMoyenne(), +estOuvert()
-- =====================================================================
CREATE SEQUENCE SEQ_LIEU START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE TABLE LIEU (
    ID NUMBER PRIMARY KEY,
    PLACE_ID VARCHAR2(150) UNIQUE,
    NOM VARCHAR2(200) NOT NULL,
    CATEGORIE_ID NUMBER NOT NULL,
    ADRESSE VARCHAR2(300) NOT NULL,
    LATITUDE NUMBER(9,6) NOT NULL,
    LONGITUDE NUMBER(9,6) NOT NULL,
    TELEPHONE VARCHAR2(50),
    SITE_WEB VARCHAR2(300),
    FOURCHETTE_PRIX VARCHAR2(20) DEFAULT '€€', -- '€', '€€', '€€€'
    HORAIRES VARCHAR2(255) DEFAULT 'Tous les jours 08:00 - 23:00',
    NOTE_MOYENNE NUMBER(3,2) DEFAULT 4.5,
    STATUT VARCHAR2(50) DEFAULT 'ACTIF', -- 'ACTIF', 'EN_ATTENTE', 'FERME'
    CONSTRAINT FK_LIEU_CATEGORIE FOREIGN KEY (CATEGORIE_ID) REFERENCES CATEGORIE(ID)
);

CREATE OR REPLACE TRIGGER TRG_LIEU
BEFORE INSERT ON LIEU FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_LIEU.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- =====================================================================
-- 6. TABLE PLAT
-- Diagramme : Plat (id, nom, description, prix, categoriePlat)
-- Relation  : Lieu (1) -- sert --> (0..*) Plat
-- =====================================================================
CREATE SEQUENCE SEQ_PLAT START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE TABLE PLAT (
    ID NUMBER PRIMARY KEY,
    LIEU_ID NUMBER NOT NULL,
    NOM VARCHAR2(150) NOT NULL,
    DESCRIPTION VARCHAR2(500),
    PRIX NUMBER(8,2) NOT NULL,
    CATEGORIE_PLAT VARCHAR2(100) DEFAULT 'Plat principal',
    CONSTRAINT FK_PLAT_LIEU FOREIGN KEY (LIEU_ID) REFERENCES LIEU(ID) ON DELETE CASCADE
);

CREATE OR REPLACE TRIGGER TRG_PLAT
BEFORE INSERT ON PLAT FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_PLAT.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- =====================================================================
-- 7. TABLE AVIS
-- Diagramme : Avis (id, note, commentaire, datePublication, statutModeration, nombreSignalements)
-- Relations : Utilisateur (1) -- rédige --> (0..*) Avis
--             Lieu (1) <-- évalue -- (0..*) Avis
-- Méthodes  : +soumettre(), +approuver(), +rejeter()
-- =====================================================================
CREATE SEQUENCE SEQ_AVIS START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE TABLE AVIS (
    ID NUMBER PRIMARY KEY,
    LIEU_ID NUMBER NOT NULL,
    UTILISATEUR_ID NUMBER NOT NULL,
    NOTE NUMBER(2) NOT NULL,
    COMMENTAIRE VARCHAR2(2000) NOT NULL,
    DATE_PUBLICATION TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    STATUT_MODERATION VARCHAR2(50) DEFAULT 'APPROUVE', -- 'EN_ATTENTE', 'APPROUVE', 'REJETE'
    NOMBRE_SIGNALEMENTS NUMBER DEFAULT 0,
    CONSTRAINT FK_AVIS_LIEU FOREIGN KEY (LIEU_ID) REFERENCES LIEU(ID) ON DELETE CASCADE,
    CONSTRAINT FK_AVIS_UTILISATEUR FOREIGN KEY (UTILISATEUR_ID) REFERENCES UTILISATEUR(ID) ON DELETE CASCADE
);

CREATE OR REPLACE TRIGGER TRG_AVIS
BEFORE INSERT ON AVIS FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_AVIS.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- =====================================================================
-- 8. TABLE PHOTO
-- Diagramme : Photo (id, url, legende, source, dateAjout, statutModeration)
-- Relations : Utilisateur (0..1) -- ajoute --> (0..*) Photo
--             Lieu (1) <-- illustre -- (0..*) Photo
-- Méthodes  : +televerser(), +redimensionner(), +approuver(), +rejeter()
-- =====================================================================
CREATE SEQUENCE SEQ_PHOTO START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE TABLE PHOTO (
    ID NUMBER PRIMARY KEY,
    LIEU_ID NUMBER NOT NULL,
    UTILISATEUR_ID NUMBER,
    URL VARCHAR2(500) NOT NULL,
    LEGENDE VARCHAR2(255),
    SOURCE VARCHAR2(50) DEFAULT 'COMMUNAUTE', -- 'COMMUNAUTE', 'PROPRIETAIRE'
    DATE_AJOUT TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    STATUT_MODERATION VARCHAR2(50) DEFAULT 'APPROUVE', -- 'EN_ATTENTE', 'APPROUVE', 'REJETE'
    CONSTRAINT FK_PHOTO_LIEU FOREIGN KEY (LIEU_ID) REFERENCES LIEU(ID) ON DELETE CASCADE,
    CONSTRAINT FK_PHOTO_UTILISATEUR FOREIGN KEY (UTILISATEUR_ID) REFERENCES UTILISATEUR(ID) ON DELETE SET NULL
);

CREATE OR REPLACE TRIGGER TRG_PHOTO
BEFORE INSERT ON PHOTO FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_PHOTO.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- =====================================================================
-- 9. TABLE LISTE_FAVORIS & ASSOCIATION FAVORIS_LIEUX
-- Diagramme : ListeFavoris (id, nom, visibilite, dateCreation)
-- Relations : Utilisateur (1) -- possède --> (0..*) ListeFavoris
--             ListeFavoris (0..*) -- regroupe --> (0..*) Lieu
-- Méthodes  : +ajouterLieu(), +retirerLieu()
-- =====================================================================
CREATE SEQUENCE SEQ_LISTE_FAVORIS START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE TABLE LISTE_FAVORIS (
    ID NUMBER PRIMARY KEY,
    UTILISATEUR_ID NUMBER NOT NULL,
    NOM VARCHAR2(150) NOT NULL,
    VISIBILITE VARCHAR2(50) DEFAULT 'PUBLIC', -- 'PUBLIC', 'PRIVE'
    DATE_CREATION TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT FK_LISTE_UTILISATEUR FOREIGN KEY (UTILISATEUR_ID) REFERENCES UTILISATEUR(ID) ON DELETE CASCADE
);

CREATE OR REPLACE TRIGGER TRG_LISTE_FAVORIS
BEFORE INSERT ON LISTE_FAVORIS FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_LISTE_FAVORIS.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- Table de liaison n..n ListeFavoris <-> Lieu
CREATE TABLE FAVORIS_LIEUX (
    LISTE_FAVORIS_ID NUMBER NOT NULL,
    LIEU_ID NUMBER NOT NULL,
    PRIMARY KEY (LISTE_FAVORIS_ID, LIEU_ID),
    CONSTRAINT FK_FL_LISTE FOREIGN KEY (LISTE_FAVORIS_ID) REFERENCES LISTE_FAVORIS(ID) ON DELETE CASCADE,
    CONSTRAINT FK_FL_LIEU FOREIGN KEY (LIEU_ID) REFERENCES LIEU(ID) ON DELETE CASCADE
);

-- =====================================================================
-- 10. TABLE ITINERAIRE
-- Diagramme : Itineraire (id, titre, date, budget, dureeTotale, lienPartage)
-- Relation  : Utilisateur (1) -- crée --> (0..*) Itineraire
-- Méthodes  : +genererProgramme(), +partager()
-- =====================================================================
CREATE SEQUENCE SEQ_ITINERAIRE START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE TABLE ITINERAIRE (
    ID NUMBER PRIMARY KEY,
    UTILISATEUR_ID NUMBER NOT NULL,
    TITRE VARCHAR2(200) NOT NULL,
    DATE_ITINERAIRE DATE DEFAULT CURRENT_DATE NOT NULL,
    BUDGET NUMBER(8,2) DEFAULT 50.0,
    DUREE_TOTALE NUMBER DEFAULT 180, -- Durée en minutes
    LIEN_PARTAGE VARCHAR2(100) UNIQUE,
    CONSTRAINT FK_ITIN_UTILISATEUR FOREIGN KEY (UTILISATEUR_ID) REFERENCES UTILISATEUR(ID) ON DELETE CASCADE
);

CREATE OR REPLACE TRIGGER TRG_ITINERAIRE
BEFORE INSERT ON ITINERAIRE FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_ITINERAIRE.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- =====================================================================
-- 11. TABLE ETAPE
-- Diagramme : Etape (id, ordre, heureArrivee, dureeVisite, modeTransport, dureeTrajet, distance)
-- Relations : Itineraire (1) -- contient --> (1..*) Etape
--             Etape (0..*) -- a pour lieu --> (1) Lieu
-- Méthodes  : +calculerTrajet()
-- =====================================================================
CREATE SEQUENCE SEQ_ETAPE START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE TABLE ETAPE (
    ID NUMBER PRIMARY KEY,
    ITINERAIRE_ID NUMBER NOT NULL,
    LIEU_ID NUMBER NOT NULL,
    ORDRE NUMBER NOT NULL,
    HEURE_ARRIVEE VARCHAR2(20), -- ex: '10:30'
    DUREE_VISITE NUMBER DEFAULT 60, -- minutes
    MODE_TRANSPORT VARCHAR2(50) DEFAULT 'PIED', -- 'PIED', 'TGM', 'METRO', 'TAXI', 'VOITURE'
    DUREE_TRAJET NUMBER DEFAULT 15, -- minutes
    DISTANCE NUMBER(6,2) DEFAULT 1.5, -- kilomètres
    CONSTRAINT FK_ETAPE_ITIN FOREIGN KEY (ITINERAIRE_ID) REFERENCES ITINERAIRE(ID) ON DELETE CASCADE,
    CONSTRAINT FK_ETAPE_LIEU FOREIGN KEY (LIEU_ID) REFERENCES LIEU(ID) ON DELETE CASCADE
);

CREATE OR REPLACE TRIGGER TRG_ETAPE
BEFORE INSERT ON ETAPE FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_ETAPE.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- =====================================================================
-- 12. TABLE EVENEMENT
-- Diagramme : Evenement (id, titre, description, dateDebut, dateFin)
-- Relation  : Lieu (1) -- organise --> (0..*) Evenement
-- =====================================================================
CREATE SEQUENCE SEQ_EVENEMENT START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE TABLE EVENEMENT (
    ID NUMBER PRIMARY KEY,
    LIEU_ID NUMBER NOT NULL,
    TITRE VARCHAR2(200) NOT NULL,
    DESCRIPTION VARCHAR2(1500),
    DATE_DEBUT TIMESTAMP NOT NULL,
    DATE_FIN TIMESTAMP NOT NULL,
    CONSTRAINT FK_EVENT_LIEU FOREIGN KEY (LIEU_ID) REFERENCES LIEU(ID) ON DELETE CASCADE
);

CREATE OR REPLACE TRIGGER TRG_EVENEMENT
BEFORE INSERT ON EVENEMENT FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_EVENEMENT.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- =====================================================================
-- 13. TABLE STATION & ASSOCIATION LIEU_STATION
-- Diagramme : Station (id, nom, type, ligne, latitude, longitude)
-- Relation  : Lieu (0..*) -- est desservi par --> (0..*) Station
-- =====================================================================
CREATE SEQUENCE SEQ_STATION START WITH 1 INCREMENT BY 1 NOCACHE;
CREATE TABLE STATION (
    ID NUMBER PRIMARY KEY,
    NOM VARCHAR2(150) NOT NULL,
    TYPE VARCHAR2(50) DEFAULT 'TGM', -- 'TGM', 'METRO', 'BUS', 'TRAIN'
    LIGNE VARCHAR2(100) DEFAULT 'Ligne Banlieue Nord TGM',
    LATITUDE NUMBER(9,6) NOT NULL,
    LONGITUDE NUMBER(9,6) NOT NULL
);

CREATE OR REPLACE TRIGGER TRG_STATION
BEFORE INSERT ON STATION FOR EACH ROW
BEGIN
    IF :NEW.ID IS NULL THEN
        SELECT SEQ_STATION.NEXTVAL INTO :NEW.ID FROM DUAL;
    END IF;
END;
/

-- Table de liaison n..n Lieu <-> Station (desserte)
CREATE TABLE LIEU_STATION (
    LIEU_ID NUMBER NOT NULL,
    STATION_ID NUMBER NOT NULL,
    PRIMARY KEY (LIEU_ID, STATION_ID),
    CONSTRAINT FK_LS_LIEU FOREIGN KEY (LIEU_ID) REFERENCES LIEU(ID) ON DELETE CASCADE,
    CONSTRAINT FK_LS_STATION FOREIGN KEY (STATION_ID) REFERENCES STATION(ID) ON DELETE CASCADE
);

-- =====================================================================
-- 14. JEU DE DONNÉES DE TEST (SEEDS) - BONS PLANS À TUNIS
-- =====================================================================

-- Utilisateurs
INSERT INTO UTILISATEUR (NOM, EMAIL, MOT_DE_PASSE, LANGUE, ROLE)
VALUES ('Administrateur TunisSpot', 'admin@tunisspot.tn', 'pbkdf2_sha256$safe_hashed_admin_pass', 'FR', 'ADMIN');

INSERT INTO UTILISATEUR (NOM, EMAIL, MOT_DE_PASSE, LANGUE, ROLE)
VALUES ('Syrine Chekki', 'syrine@tunisspot.tn', 'pbkdf2_sha256$safe_hashed_visiteur_pass', 'FR', 'VISITEUR');

INSERT INTO UTILISATEUR (NOM, EMAIL, MOT_DE_PASSE, LANGUE, ROLE)
VALUES ('Karim Propriétaire Restaurant Le Golfe', 'karim@legolfe.tn', 'pbkdf2_sha256$safe_hashed_etab_pass', 'FR', 'PROPRIETAIRE');

-- Préférences
INSERT INTO PREFERENCE (UTILISATEUR_ID, BUDGET_MAX, AMBIANCES, REGIMES)
VALUES (2, 80.0, 'terrasse,vue_mer,romantique', 'halal');

-- Notifications
INSERT INTO NOTIFICATION (UTILISATEUR_ID, TITRE, MESSAGE, EST_LUE)
VALUES (2, 'Bienvenue sur TunisSpot !', 'Découvrez les meilleurs cafés et restaurants du Grand Tunis.', 1);

INSERT INTO NOTIFICATION (UTILISATEUR_ID, TITRE, MESSAGE, EST_LUE)
VALUES (1, 'Nouveau lieu soumis', 'Syrine Chekki a soumis un nouveau spot pour validation.', 0);

-- Catégories
INSERT INTO CATEGORIE (LIBELLE, ICONE) VALUES ('Restaurants & Gastronomie', 'fa-utensils');
INSERT INTO CATEGORIE (LIBELLE, ICONE) VALUES ('Cafés & Salons de thé', 'fa-coffee');
INSERT INTO CATEGORIE (LIBELLE, ICONE) VALUES ('Culture & Patrimoine', 'fa-landmark');

-- Lieux
INSERT INTO LIEU (PLACE_ID, NOM, CATEGORIE_ID, ADRESSE, LATITUDE, LONGITUDE, TELEPHONE, SITE_WEB, FOURCHETTE_PRIX, HORAIRES, NOTE_MOYENNE, STATUT)
VALUES ('place_cafe_delices', 'Café des Délices', 2, 'Rue Sidi Bou Farès, Sidi Bou Saïd', 36.871200, 10.346800, '+216 71 749 923', 'https://cafedesdelices.tn', '€€', 'Tous les jours 08:30 - 00:00', 4.7, 'ACTIF');

INSERT INTO LIEU (PLACE_ID, NOM, CATEGORIE_ID, ADRESSE, LATITUDE, LONGITUDE, TELEPHONE, SITE_WEB, FOURCHETTE_PRIX, HORAIRES, NOTE_MOYENNE, STATUT)
VALUES ('place_resto_golfe', 'Restaurant Le Golfe', 1, '5 Rue El Arbi Zarrouk, La Marsa Plage', 36.882500, 10.329800, '+216 71 748 205', 'https://legolfe.tn', '€€€', '12:00 - 23:30', 4.8, 'ACTIF');

INSERT INTO LIEU (PLACE_ID, NOM, CATEGORIE_ID, ADRESSE, LATITUDE, LONGITUDE, TELEPHONE, SITE_WEB, FOURCHETTE_PRIX, HORAIRES, NOTE_MOYENNE, STATUT)
VALUES ('place_dar_el_jeld', 'Dar El Jeld Hôtel & Spa', 1, '5-10 Rue Dar El Jeld, Médina de Tunis', 36.798900, 10.169800, '+216 70 016 190', 'https://dareljeld.com', '€€€', '12:30 - 23:00', 4.9, 'ACTIF');

-- Plats
INSERT INTO PLAT (LIEU_ID, NOM, DESCRIPTION, PRIX, CATEGORIE_PLAT)
VALUES (1, 'Thé aux pignons de Sidi Bou Saïd', 'Thé vert à la menthe fraîche servi avec généreuse poignée de pignons.', 8.50, 'Boissons');

INSERT INTO PLAT (LIEU_ID, NOM, DESCRIPTION, PRIX, CATEGORIE_PLAT)
VALUES (1, 'Bambalouni traditionnel au sucre', 'Beignet chaud préparé selon la recette ancestrale du village.', 2.50, 'Desserts');

INSERT INTO PLAT (LIEU_ID, NOM, DESCRIPTION, PRIX, CATEGORIE_PLAT)
VALUES (2, 'Couscous royal au Mérou sauvage', 'Semoule fine cuite à la vapeur et mérou frais pêché sur les côtes de La Marsa.', 48.00, 'Plat principal');

INSERT INTO PLAT (LIEU_ID, NOM, DESCRIPTION, PRIX, CATEGORIE_PLAT)
VALUES (3, 'Tajine Malsouka à la volaille', 'Feuilles de brik croustillantes farcies au poulet fermier et amandes.', 24.00, 'Entrée');

-- Avis
INSERT INTO AVIS (LIEU_ID, UTILISATEUR_ID, NOTE, COMMENTAIRE, STATUT_MODERATION, NOMBRE_SIGNALEMENTS)
VALUES (1, 2, 5, 'Vue à couper le souffle sur le golfe de Tunis ! Le coucher de soleil est magique.', 'APPROUVE', 0);

INSERT INTO AVIS (LIEU_ID, UTILISATEUR_ID, NOTE, COMMENTAIRE, STATUT_MODERATION, NOMBRE_SIGNALEMENTS)
VALUES (2, 2, 5, 'Service irréprochable et poisson d une fraîcheur exceptionnelle les pieds dans l eau.', 'APPROUVE', 0);

-- Photos
INSERT INTO PHOTO (LIEU_ID, UTILISATEUR_ID, URL, LEGENDE, SOURCE, STATUT_MODERATION)
VALUES (1, 2, 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62', 'Terrasse mythique du Café des Délices', 'COMMUNAUTE', 'APPROUVE');

INSERT INTO PHOTO (LIEU_ID, UTILISATEUR_ID, URL, LEGENDE, SOURCE, STATUT_MODERATION)
VALUES (2, 3, 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5', 'Salle gastronomique avec vue panoramique mer', 'PROPRIETAIRE', 'APPROUVE');

-- Listes de Favoris & Lieux associés
INSERT INTO LISTE_FAVORIS (UTILISATEUR_ID, NOM, VISIBILITE)
VALUES (2, 'Mes coups de cœur de la Banlieue Nord', 'PUBLIC');

INSERT INTO FAVORIS_LIEUX (LISTE_FAVORIS_ID, LIEU_ID) VALUES (1, 1);
INSERT INTO FAVORIS_LIEUX (LISTE_FAVORIS_ID, LIEU_ID) VALUES (1, 2);

-- Itinéraire & Étapes
INSERT INTO ITINERAIRE (UTILISATEUR_ID, TITRE, DATE_ITINERAIRE, BUDGET, DUREE_TOTALE, LIEN_PARTAGE)
VALUES (2, 'Une journée parfaite à Sidi Bou Saïd et La Marsa', CURRENT_DATE, 75.0, 240, 'itin_sidi_bou_marsa_2026');

INSERT INTO ETAPE (ITINERAIRE_ID, LIEU_ID, ORDRE, HEURE_ARRIVEE, DUREE_VISITE, MODE_TRANSPORT, DUREE_TRAJET, DISTANCE)
VALUES (1, 1, 1, '10:00', 90, 'TGM', 20, 15.0);

INSERT INTO ETAPE (ITINERAIRE_ID, LIEU_ID, ORDRE, HEURE_ARRIVEE, DUREE_VISITE, MODE_TRANSPORT, DUREE_TRAJET, DISTANCE)
VALUES (1, 2, 2, '12:30', 120, 'PIED', 25, 2.3);

-- Événements
INSERT INTO EVENEMENT (LIEU_ID, TITRE, DESCRIPTION, DATE_DEBUT, DATE_FIN)
VALUES (1, 'Soirée Malouf & Musique Traditionnelle', 'Concert acoustique de Malouf tunisien face à la mer.', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '3' HOUR);

INSERT INTO EVENEMENT (LIEU_ID, TITRE, DESCRIPTION, DATE_DEBUT, DATE_FIN)
VALUES (2, 'Soirée Jazz & Fruits de Mer', 'Dégustation gastronomique et trio jazz en direct.', CURRENT_TIMESTAMP + INTERVAL '1' DAY, CURRENT_TIMESTAMP + INTERVAL '1' DAY + INTERVAL '4' HOUR);

-- Stations de transport & Dessertes
INSERT INTO STATION (NOM, TYPE, LIGNE, LATITUDE, LONGITUDE)
VALUES ('Station Sidi Bou Saïd', 'TGM', 'Ligne Banlieue Nord TGM', 36.868200, 10.339500);

INSERT INTO STATION (NOM, TYPE, LIGNE, LATITUDE, LONGITUDE)
VALUES ('Station Marsa Plage', 'TGM', 'Ligne Banlieue Nord TGM', 36.879500, 10.327500);

INSERT INTO LIEU_STATION (LIEU_ID, STATION_ID) VALUES (1, 1);
INSERT INTO LIEU_STATION (LIEU_ID, STATION_ID) VALUES (2, 2);

COMMIT;

-- =====================================================================
-- 15. VÉRIFICATION DU CHARGEMENT DES 13 TABLES DU DIAGRAMME
-- =====================================================================
SELECT table_name FROM user_tables 
WHERE table_name IN (
    'UTILISATEUR', 'PREFERENCE', 'NOTIFICATION', 'CATEGORIE', 
    'LIEU', 'PLAT', 'AVIS', 'PHOTO', 'LISTE_FAVORIS', 
    'FAVORIS_LIEUX', 'ITINERAIRE', 'ETAPE', 'EVENEMENT', 
    'STATION', 'LIEU_STATION'
)
ORDER BY table_name;
