# 🇹🇳 TunisSpot — Plateforme de Loisirs, Découverte & Bons Plans à Tunis

Inspiré par le design épuré, dynamique et lifestyle de **Win Tokhrej** (*wintokhrej.com*), **TunisSpot** est une application web moderne développée avec **Django** et modélisée pour une base de données relationnelle **Oracle SQL Developer**.

---

## 📋 Présentation du Projet & Architecture

Ce projet implémente l'intégralité des **6 modules** et des fonctionnalités spécifiées dans le cahier des charges officiel de TunisSpot (septembre 2026), avec tous les CRUDs fonctionnels :

### 1. Module 1 : Utilisateurs, Profils & Passeport de Découverte
* Inscription, connexion, gestion de profil (avatar, langue FR / EN / AR, téléphone).
* Gestion des rôles : `Visiteur`, `Touriste`, `Résident`, `Propriétaire d'établissement`, `Modérateur`, `Admin`.
* **Passeport de découverte (Gamification)** : jauge de progression, cumul de points (ex: +30 pts pour un spot, +15 pts pour un avis), déblocage automatique de badges (*Explorateur de la Médina*, *Roi du Café & Thé*, *Guide Local Certifié*, *Chasseur de Pépites*).
* Profil de préférences de sortie : budget maximum (DT), ambiances préférées (romantique, terrasse, vue mer...), régimes alimentaires (halal, végétarien...).
* Centre de notifications interactif.

### 2. Module 2 : Lieux, Établissements & Pépites Locales
* **CRUD complet** des lieux et établissements (Créer, Consulter, Modifier, Supprimer).
* Catégories avec icônes et quartiers emblématiques du Grand Tunis (Sidi Bou Saïd, La Marsa, Médina de Tunis, Carthage, Gammarth, Les Berges du Lac...).
* **Label « Pépite Locale »** : algorithme distinguant les adresses authentiques plébiscitées par les résidents tunisiens (note > 4.2 et majorité d'avis de résidents).
* Indice de foule estimé en temps réel (*Calme*, *Moyen*, *Élevé*).
* Recherche multi-critères et filtres avancés : budget (€, €€, €€€), terrasse, vue mer, Wi-Fi, accès PMR, climatisation, halal, options végétariennes.
* **Fonctionnalité signature « Laisse le hasard choisir ta sortie ! 🎲 »** (Roulette aléatoire de spot avec tirage immédiat par quartier).
* Cartographie interactive **Leaflet / OpenStreetMap** avec bascule Grille / Carte.
* Procédure de revendication de fiche pour les gérants et propriétaires.

### 3. Module 3 : Avis, Photos et Menus Numériques
* **CRUD complet des Menus numériques** : ajout de plats, spécialités tunisiennes, boissons et desserts avec tarifs en Dinars Tunisiens (DT).
* Publication d'avis avec notation multi-critères : *Qualité*, *Service*, *Rapport Qualité/Prix*, *Ambiance*.
* **Score de confiance des avis** calculé selon l'ancienneté du compte et la complétude de l'évaluation, pondérant automatiquement la note globale du lieu.
* Distinction claire entre avis de résidents locaux et de touristes.
* Signalement de contenus inappropriés ou d'informations obsolètes.

### 4. Module 4 : Transports et Mobilité Multimodale
* Base de données complète des transports du Grand Tunis : **TGM**, **Métro Léger**, **Taxis/VTC (Bolt, OTaxi)**, **Voiture**, **Marche à pied**.
* Lignes et stations avec coordonnées GPS précises (Tunis Marine, La Goulette, Carthage Byrsa, Sidi Bou Saïd, Marsa Plage...).
* **Comparateur Multimodal Intelligent** : calcul de distance (formule de Haversine), durée estimée et estimation du coût en Dinars Tunisiens (DT) avec recommandation automatique (*« Le plus rapide »*, *« Le moins cher »*, *« Le plus écologique »*).

### 5. Module 5 : Itinéraires & Planning de Sorties
* **Générateur de Journée Parfaite** : l'utilisateur choisit son temps (Matinée, Après-midi, Journée complète), son budget et son ambiance (Romantique, Culture & Médina, Détente bord de mer, Foodie) ; le système compose automatiquement un programme optimisé étape par étape.
* **CRUD Itinéraires & Étapes** : création manuelle de parcours avec ordre des visites, durées et modes de transport.
* Génération de liens de partage uniques pour envoyer ses itinéraires à ses proches.
* **Listes de favoris personnalisées** (bouton coup de cœur ❤️).
* **Sorties de groupe avec système de vote** : création d'une sortie avec code d'invitation, proposition de lieux par les participants et vote interactif.

### 6. Module 6 : Événements, Partenaires & Dashboards
* Agenda culturel et festif (concerts, expositions, soirées rooftops, festivals).
* Offres et promotions exclusives négociées avec les partenaires (-15%, réductions midi, codes promos).
* **Back-Office d'Administration & Modération** : métriques clés, modération des avis et photos, validation des revendications de fiches propriétaires, gestion des signalements.
* **Tableau de bord Propriétaire** : statistiques de vues, clics sur itinéraire, ajouts aux favoris et consultations de menu.

---

## 🗄️ Schéma de Base de Données (SQL Developer)

Le fichier `tunisspot_tables_sqldeveloper.sql` contient le script DDL complet directement compatible avec **Oracle SQL Developer** et les SGBD relationnels :
* Définition de toutes les tables : `UTILISATEUR`, `PREFERENCE`, `BADGE`, `USER_BADGE`, `NOTIFICATION`, `CATEGORIE`, `QUARTIER`, `LIEU`, `PLAT`, `AVIS`, `PHOTO`, `REVENDICATION`, `SIGNALEMENT`, `MOYEN_TRANSPORT`, `LIGNE`, `STATION`, `LIEU_STATION`, `TRAJET_HISTORIQUE`, `LISTE_FAVORIS`, `ITINERAIRE`, `ETAPE`, `SORTIE_GROUPE`, `PROPOSITION_LIEU`, `VOTE_SORTIE`, `PARTENAIRE`, `EVENEMENT`, `OFFRE_PROMOTION`, `STATISTIQUE_FICHE`.
* Clés primaires générées automatiquement (`IDENTITY`).
* Clés étrangères avec suppression en cascade ou contraintes d'intégrité référentielle.
* Contraintes de validation (`CHECK`).

---

## 🚀 Démarrage Rapide

### 1. Prérequis
* Python 3.10+ (ou version supérieure, testé avec Python 3.14)
* Django 5+ / 6+

### 2. Initialisation de la base et données de test
La base de données SQLite embarquée est déjà configurée et peuplée avec des données de démonstration du Grand Tunis. Si vous souhaitez réinitialiser :
```bash
python manage.py migrate
python seed_tunisspot.py
```

### 3. Lancer le serveur local
```bash
python manage.py runserver
```
Rendez-vous ensuite sur : **`http://127.0.0.1:8000/`**

---

## 🔑 Comptes de Démonstration Pré-configurés

| Identifiant | Mot de passe | Rôle | Privilèges & Accès |
|---|---|---|---|
| `admin` | `admin123` | **Administrateur** | Accès Back-Office complet (`/dashboard/admin/`), Django Admin (`/admin/`), tous les CRUDs |
| `syrine` | `syrine123` | **Résident & Guide Local** | 320 points, Badges débloqués, créatrice d'itinéraires et listes de favoris |
| `amine` | `amine123` | **Résident** | 280 points, Badge Roi du Café & Pépites |
| `karim_proprio` | `karim123` | **Propriétaire d'Établissement** | Accès Espace Pro (`/dashboard/pro/`), gestion des menus et offres de son resto (*Le Golfe*) |
| `emma_tourist` | `touriste123` | **Touriste** | Profil touriste, avis et calculs d'itinéraires |

---

## 🧪 Tests Unitaires et Validation
Pour exécuter l'ensemble de la suite de tests automatisés validant toutes les URLs et opérations CRUD :
```bash
python test_all_views.py
python test_crud_operations.py
```
*(Résultat : 100% des tests validés)*
