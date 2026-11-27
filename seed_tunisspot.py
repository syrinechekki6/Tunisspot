import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tunisspot.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from users.models import Utilisateur, Preference, Badge, UserBadge, Notification
from spots.models import Categorie, Quartier, Lieu, Plat, Avis, Photo, Revendication, Signalement
from transports.models import MoyenTransport, Ligne, Station, LieuStation, TrajetHistorique
from itineraries.models import ListeFavoris, Itineraire, Etape, SortieGroupe, PropositionLieu, Vote
from events.models import Evenement, Partenaire, OffrePromotion, StatistiqueFiche

def seed():
    print("=== Début du peuplement de la base TunisSpot ===")

    # 1. Utilisateurs
    admin_user, _ = Utilisateur.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@tunisspot.tn',
            'nom': 'Administrateur TunisSpot',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
            'points': 500,
            'est_guide_local': True,
            'langue': 'FR'
        }
    )
    admin_user.set_password('admin123')
    admin_user.save()

    syrine, _ = Utilisateur.objects.get_or_create(
        username='syrine',
        defaults={
            'email': 'syrine@tunisspot.tn',
            'nom': 'Syrine Chekki',
            'role': 'RESIDENT',
            'points': 320,
            'est_guide_local': True,
            'langue': 'FR'
        }
    )
    syrine.set_password('syrine123')
    syrine.save()

    amine, _ = Utilisateur.objects.get_or_create(
        username='amine',
        defaults={
            'email': 'amine@tunisspot.tn',
            'nom': 'Amine Salhi',
            'role': 'RESIDENT',
            'points': 280,
            'est_guide_local': True,
            'langue': 'FR'
        }
    )
    amine.set_password('amine123')
    amine.save()

    karim_proprio, _ = Utilisateur.objects.get_or_create(
        username='karim_proprio',
        defaults={
            'email': 'karim@restogolfe.tn',
            'nom': 'Karim Ben Salem',
            'role': 'PROPRIETAIRE',
            'points': 150,
            'langue': 'FR'
        }
    )
    karim_proprio.set_password('karim123')
    karim_proprio.save()

    touriste_emma, _ = Utilisateur.objects.get_or_create(
        username='emma_tourist',
        defaults={
            'email': 'emma@voyage.fr',
            'nom': 'Emma Dubois',
            'role': 'TOURISTE',
            'points': 80,
            'langue': 'FR'
        }
    )
    touriste_emma.set_password('touriste123')
    touriste_emma.save()

    # Préférences
    for u in [admin_user, syrine, amine, karim_proprio, touriste_emma]:
        Preference.objects.get_or_create(
            user=u,
            defaults={
                'budget_max': 80.0,
                'ambiances': 'romantique,terrasse,calme,vue_mer',
                'regimes': 'halal'
            }
        )

    # Badges
    b1, _ = Badge.objects.get_or_create(nom="Explorateur de la Médina", defaults={'description': "A visité et noté au moins 3 lieux historiques de la Médina", 'icone': 'fa-landmark', 'points_requis': 100})
    b2, _ = Badge.objects.get_or_create(nom="Roi du Café & Thé", defaults={'description': "Grand amateur de cafés traditionnels et salons branchés", 'icone': 'fa-coffee', 'points_requis': 150})
    b3, _ = Badge.objects.get_or_create(nom="Guide Local Certifié", defaults={'description': "Contributeur exemplaire certifié par TunisSpot", 'icone': 'fa-certificate', 'points_requis': 250})
    b4, _ = Badge.objects.get_or_create(nom="Chasseur de Pépites", defaults={'description': "A déniché des adresses authentiques hors des sentiers battus", 'icone': 'fa-gem', 'points_requis': 200})

    UserBadge.objects.get_or_create(user=syrine, badge=b1)
    UserBadge.objects.get_or_create(user=syrine, badge=b3)
    UserBadge.objects.get_or_create(user=amine, badge=b2)
    UserBadge.objects.get_or_create(user=amine, badge=b4)

    # 2. Catégories
    cat_resto, _ = Categorie.objects.get_or_create(libelle="Restaurants & Gastronomie", defaults={'libelle_ar': 'مطاعم ومأكولات', 'libelle_en': 'Restaurants & Dining', 'icone': 'fa-utensils', 'slug': 'restaurants', 'image_couverture': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80'})
    cat_cafe, _ = Categorie.objects.get_or_create(libelle="Cafés & Salons de thé", defaults={'libelle_ar': 'مقاهي وشاي', 'libelle_en': 'Cafes & Tea Rooms', 'icone': 'fa-coffee', 'slug': 'cafes', 'image_couverture': 'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=800&q=80'})
    cat_cult, _ = Categorie.objects.get_or_create(libelle="Culture & Patrimoine", defaults={'libelle_ar': 'ثقافة وتراث', 'libelle_en': 'Culture & Heritage', 'icone': 'fa-landmark', 'slug': 'culture', 'image_couverture': 'https://images.unsplash.com/photo-1584646098378-0874589d76b1?auto=format&fit=crop&w=800&q=80'})
    cat_rooftop, _ = Categorie.objects.get_or_create(libelle="Rooftops & Sorties", defaults={'libelle_ar': 'إطلالات وسهرات', 'libelle_en': 'Rooftops & Nightlife', 'icone': 'fa-cocktail', 'slug': 'rooftops', 'image_couverture': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80'})
    cat_activite, _ = Categorie.objects.get_or_create(libelle="Activités & Plages", defaults={'libelle_ar': 'أنشطة وشواطئ', 'libelle_en': 'Activities & Beaches', 'icone': 'fa-umbrella-beach', 'slug': 'activites', 'image_couverture': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80'})

    # Quartiers
    q_sidi, _ = Quartier.objects.get_or_create(nom="Sidi Bou Saïd", defaults={'latitude': 36.8708, 'longitude': 10.3422, 'description': "Le village perché aux façades blanches et volets bleus surplombant le golfe."})
    q_marsa, _ = Quartier.objects.get_or_create(nom="La Marsa", defaults={'latitude': 36.8782, 'longitude': 10.3247, 'description': "Bord de mer élégant, cafés branchés, plage et promenades gourmandes."})
    q_carthage, _ = Quartier.objects.get_or_create(nom="Carthage", defaults={'latitude': 36.8528, 'longitude': 10.3242, 'description': "Cité millénaire punique et romaine, sites archéologiques et villas verdoyantes."})
    q_medina, _ = Quartier.objects.get_or_create(nom="Médina de Tunis", defaults={'latitude': 36.7992, 'longitude': 10.1706, 'description': "Classée UNESCO, ruelles vivantes, souks parfumés et palais cachés."})
    q_gammarth, _ = Quartier.objects.get_or_create(nom="Gammarth", defaults={'latitude': 36.9142, 'longitude': 10.2981, 'description': "Collines côtières, hôtels de luxe, restaurants raffinés et rooftops branchés."})
    q_lac, _ = Quartier.objects.get_or_create(nom="Les Berges du Lac", defaults={'latitude': 36.8354, 'longitude': 10.2372, 'description': "Quartier moderne des affaires, restaurants chics et promenades au bord de l'eau."})

    # 3. Lieux (Spots)
    lieu1, _ = Lieu.objects.get_or_create(
        nom="Café des Délices",
        defaults={
            'slug': 'cafe-des-delices-sidi-bou-said',
            'categorie': cat_cafe,
            'quartier': q_sidi,
            'adresse': 'Rue Sidi Bou Fares, Sidi Bou Saïd',
            'latitude': 36.8712,
            'longitude': 10.3468,
            'telephone': '+216 71 749 550',
            'site_web': 'https://sidi-bou-said.tn',
            'fourchette_prix': '€€',
            'prix_moyen': 18.0,
            'horaires': 'Tous les jours de 08:30 à 00:00',
            'description': "Le café mythique immortalisé par Patrick Bruel. Terrasse en gradins offrant une vue panoramique à couper le souffle sur le golfe de Tunis et le port de plaisance. Dégustez-y un thé aux pignons avec un bambalouni encore chaud au coucher du soleil.",
            'image_principale': 'https://images.unsplash.com/photo-1544644181-1484b3fdfc62?auto=format&fit=crop&w=1000&q=80',
            'note_moyenne': 4.7,
            'nombre_avis': 48,
            'est_pepite_locale': False,
            'indice_foule': 'Élevé',
            'terrasse': True,
            'vue_mer': True,
            'ambiance_romantique': True,
            'wifi': True,
            'parking': False
        }
    )

    lieu2, _ = Lieu.objects.get_or_create(
        nom="Kahwet El Alia (Café des Nattes)",
        defaults={
            'slug': 'cafe-des-nattes-sidi-bou-said',
            'categorie': cat_cafe,
            'quartier': q_sidi,
            'adresse': 'Place du Village, Sidi Bou Saïd',
            'latitude': 36.8703,
            'longitude': 10.3415,
            'telephone': '+216 71 740 012',
            'fourchette_prix': '€',
            'prix_moyen': 7.0,
            'horaires': '07:00 - 23:00',
            'description': "Véritable institution historique au sommet du grand escalier de Sidi Bou Saïd. Déchaussez-vous pour vous asseoir sur les nattes traditionnelles en jonc et siroter un authentique thé vert à la menthe et aux pignons parfumé à la fleur d'oranger.",
            'image_principale': 'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=1000&q=80',
            'note_moyenne': 4.8,
            'nombre_avis': 62,
            'est_pepite_locale': True,
            'indice_foule': 'Moyen',
            'terrasse': True,
            'vue_mer': False,
            'ambiance_amis': True,
            'wifi': False
        }
    )

    lieu3, _ = Lieu.objects.get_or_create(
        nom="Restaurant Le Golfe",
        defaults={
            'slug': 'restaurant-le-golfe-la-marsa',
            'categorie': cat_resto,
            'quartier': q_marsa,
            'adresse': '5 Rue El Arbi Zarrouk, La Marsa Plage',
            'latitude': 36.8825,
            'longitude': 10.3298,
            'telephone': '+216 71 748 219',
            'site_web': 'https://legolfe.com.tn',
            'fourchette_prix': '€€€',
            'prix_moyen': 65.0,
            'horaires': 'Midi et Soir (12:00 - 23:30)',
            'description': "Adresse gastronomique emblématique de La Marsa les pieds dans le sable. Poissons ultra frais grillés au feu de bois, carpaccios raffinés, couscous au mérou royal et terrasse panoramique baignée par les embruns marins.",
            'image_principale': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1000&q=80',
            'note_moyenne': 4.6,
            'nombre_avis': 39,
            'est_pepite_locale': False,
            'indice_foule': 'Moyen',
            'terrasse': True,
            'vue_mer': True,
            'parking': True,
            'ambiance_romantique': True,
            'proprietaire': karim_proprio
        }
    )

    lieu4, _ = Lieu.objects.get_or_create(
        nom="Fondouk El Attarine",
        defaults={
            'slug': 'fondouk-el-attarine-medina',
            'categorie': cat_resto,
            'quartier': q_medina,
            'adresse': '9 Bis Souk El Attarine, Médina de Tunis',
            'latitude': 36.7988,
            'longitude': 10.1708,
            'telephone': '+216 71 322 245',
            'fourchette_prix': '€€',
            'prix_moyen': 38.0,
            'horaires': 'Du mardi au dimanche de 12:00 à 18:00',
            'description': "Un caravansérail du XVIIe siècle restauré avec un goût exquis au cœur du Souk des parfumeurs. Patio lumineux, fontaine murmurante, plats tunisiens revisités avec amour (borzgane, tajine malsouka, salade omek houria) et boutique d'artisanat chic.",
            'image_principale': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1000&q=80',
            'note_moyenne': 4.9,
            'nombre_avis': 53,
            'est_pepite_locale': True,
            'indice_foule': 'Moyen',
            'terrasse': True,
            'ambiance_romantique': True,
            'ambiance_famille': True,
            'vegetarien': True
        }
    )

    lieu5, _ = Lieu.objects.get_or_create(
        nom="Thermes d'Antonin de Carthage",
        defaults={
            'slug': 'thermes-antonin-carthage',
            'categorie': cat_cult,
            'quartier': q_carthage,
            'adresse': 'Site Archéologique de Carthage, Rue des Thermes',
            'latitude': 36.8532,
            'longitude': 10.3347,
            'telephone': '+216 71 730 036',
            'fourchette_prix': '€',
            'prix_moyen': 12.0,
            'horaires': 'Tous les jours 08:30 - 17:30',
            'description': "Le plus grand ensemble thermal romain construit sur le sol africain et le troisième du monde romain. Situé en bord de mer avec les colonnes grandioses se détachant sur le bleu azur de la Méditerranée.",
            'image_principale': 'https://images.unsplash.com/photo-1584646098378-0874589d76b1?auto=format&fit=crop&w=1000&q=80',
            'note_moyenne': 4.8,
            'nombre_avis': 75,
            'est_pepite_locale': False,
            'indice_foule': 'Faible',
            'vue_mer': True,
            'acces_pmr': True,
            'ambiance_famille': True
        }
    )

    lieu6, _ = Lieu.objects.get_or_create(
        nom="The View Rooftop Gammarth",
        defaults={
            'slug': 'the-view-rooftop-gammarth',
            'categorie': cat_rooftop,
            'quartier': q_gammarth,
            'adresse': 'Zone Touristique Les Côtes de Carthage, Gammarth',
            'latitude': 36.9155,
            'longitude': 10.2975,
            'telephone': '+216 71 911 100',
            'fourchette_prix': '€€€',
            'prix_moyen': 55.0,
            'horaires': '17:00 - 02:00',
            'description': "Le rooftop le plus en vogue des nuits tunisoises. Vue plongeante sur les collines boisées et la baie de Gammarth. Cocktails création, tapas méditerranéennes et programmation musicale soignée pour des couchers de soleil inoubliables.",
            'image_principale': 'https://images.unsplash.com/photo-1572116469696-31de0f17cc34?auto=format&fit=crop&w=1000&q=80',
            'note_moyenne': 4.5,
            'nombre_avis': 31,
            'est_pepite_locale': False,
            'indice_foule': 'Élevé',
            'terrasse': True,
            'vue_mer': True,
            'ambiance_amis': True,
            'ambiance_romantique': True,
            'parking': True
        }
    )

    lieu7, _ = Lieu.objects.get_or_create(
        nom="Le Saf-Saf La Marsa",
        defaults={
            'slug': 'le-saf-saf-la-marsa',
            'categorie': cat_cafe,
            'quartier': q_marsa,
            'adresse': 'Place du Saf-Saf, La Marsa',
            'latitude': 36.8785,
            'longitude': 10.3235,
            'telephone': '+216 71 740 500',
            'fourchette_prix': '€',
            'prix_moyen': 6.0,
            'horaires': '07:30 - 23:00',
            'description': "Un lieu chargé d'histoire au cœur de La Marsa, organisé autour d'une cour ombragée et de son puits séculaire actionné par une chamelle. On y déguste de délicieux brick à l'oeuf, du thé à la menthe et des glaces artisanales dans une atmosphère familiale unique.",
            'image_principale': 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=1000&q=80',
            'note_moyenne': 4.6,
            'nombre_avis': 58,
            'est_pepite_locale': True,
            'indice_foule': 'Élevé',
            'terrasse': True,
            'ambiance_famille': True,
            'ambiance_amis': True
        }
    )

    lieu8, _ = Lieu.objects.get_or_create(
        nom="Dar El Jeld Restaurant & Spa",
        defaults={
            'slug': 'dar-el-jeld-medina',
            'categorie': cat_resto,
            'quartier': q_medina,
            'adresse': '5-10 Rue Dar El Jeld, Médina de Tunis',
            'latitude': 36.7997,
            'longitude': 10.1691,
            'telephone': '+216 71 260 916',
            'site_web': 'https://dareljeld.com',
            'fourchette_prix': '€€€',
            'prix_moyen': 85.0,
            'horaires': '12:30 - 15:00 / 19:30 - 23:00',
            'description': "Le temple absolu de la gastronomie tunisienne patrimoniale. Installé dans un palais majestueux aux stucs sculptés, faïences d'époque et patio orné de lustres en cristal. Une expérience culinaire de haut vol saluée par les guides internationaux.",
            'image_principale': 'https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1000&q=80',
            'note_moyenne': 4.9,
            'nombre_avis': 84,
            'est_pepite_locale': True,
            'indice_foule': 'Moyen',
            'ambiance_romantique': True,
            'climatisation': True,
            'vegetarien': True
        }
    )

    # 4. Plats pour les menus numériques
    # Plats pour Le Golfe
    Plat.objects.get_or_create(lieu=lieu3, nom="Couscous Royal au Mérou Sauvage", defaults={'prix': 48.0, 'categorie_plat': 'Spécialité Tunisienne', 'description': "Semoule fine cuite à la vapeur de poisson, pavé de mérou frais, légumes de saison confits et piment frit.", 'est_populaire': True})
    Plat.objects.get_or_create(lieu=lieu3, nom="Carpaccio de Loup de Mer aux Agrumes de Nabeul", defaults={'prix': 28.0, 'categorie_plat': 'Entrée', 'description': "Fines tranches de loup mariné, huile d'olive vierge bio de Teboursouk et suprêmes d'orange.", 'est_populaire': False})
    Plat.objects.get_or_create(lieu=lieu3, nom="Daurade Royale grillée au feu de bois", defaults={'prix': 42.0, 'categorie_plat': 'Plat principal', 'description': "Servie avec tastira tunisienne et pommes de terre rissolées au romarin.", 'est_populaire': True})

    # Plats pour Fondouk El Attarine
    Plat.objects.get_or_create(lieu=lieu4, nom="Tajine Malsouka à la volaille fermière", defaults={'prix': 18.0, 'categorie_plat': 'Entrée', 'description': "Feuilleté traditionnel croustillant garni d'effiloché de poulet, fromage et œufs fermiers.", 'est_populaire': True})
    Plat.objects.get_or_create(lieu=lieu4, nom="Ojja aux Crevettes Royales de La Goulette", defaults={'prix': 26.0, 'categorie_plat': 'Spécialité Tunisienne', 'description': "Mijoté de tomates fraîches, ail, harissa berbère et crevettes sautées.", 'est_populaire': True})
    Plat.objects.get_or_create(lieu=lieu4, nom="Assiette Gourmande de Salades Tunisiennes", defaults={'prix': 15.0, 'categorie_plat': 'Entrée', 'description': "Méchouia au feu de bois, houria de carottes aux épices, salade tunisienne croquante.", 'est_populaire': False})
    Plat.objects.get_or_create(lieu=lieu4, nom="Crème Assida Zgougou maison", defaults={'prix': 10.0, 'categorie_plat': 'Dessert', 'description': "Crème onctueuse de pin d'Alep surmontée de fruits secs torréfiés.", 'est_populaire': True})

    # Plats pour Café des Délices
    Plat.objects.get_or_create(lieu=lieu1, nom="Thé Vert à la Menthe Fraîche & Pignons", defaults={'prix': 8.5, 'categorie_plat': 'Boisson', 'description': "Servi dans le verre traditionnel garni généreusement de pignons dorés.", 'est_populaire': True})
    Plat.objects.get_or_create(lieu=lieu1, nom="Bambalouni chaud de Sidi Bou Saïd", defaults={'prix': 3.5, 'categorie_plat': 'Dessert', 'description': "Le fameux beignet tunisien saupoudré de sucre fin.", 'est_populaire': True})
    Plat.objects.get_or_create(lieu=lieu1, nom="Café Turc parfumé à l'Eau de Fleur d'Oranger", defaults={'prix': 6.0, 'categorie_plat': 'Boisson', 'description': "Préparé selon la recette ancestrale dans un cezve en cuivre.", 'est_populaire': False})

    # 5. Avis avec critères et score de confiance
    a1, _ = Avis.objects.get_or_create(
        lieu=lieu1, user=touriste_emma,
        defaults={
            'note': 5,
            'note_qualite': 5,
            'note_service': 4,
            'note_prix': 4,
            'note_ambiance': 5,
            'commentaire': "Une vue extraordinaire sur la mer Méditerranée ! Le thé aux pignons et le bambalouni étaient parfaits. À faire absolument au coucher du soleil.",
            'score_confiance': 0.85,
            'type_visiteur': 'TOURISTE'
        }
    )

    a2, _ = Avis.objects.get_or_create(
        lieu=lieu2, user=syrine,
        defaults={
            'note': 5,
            'note_qualite': 5,
            'note_service': 5,
            'note_prix': 5,
            'note_ambiance': 5,
            'commentaire': "Le vrai cœur de Sidi Bou Saïd ! Les nattes, l'odeur du jasmin et le café turc traditionnel... C'est la pépite authentique que beaucoup de touristes ratent en restant au café d'à côté.",
            'score_confiance': 1.0,
            'type_visiteur': 'RESIDENT'
        }
    )

    a3, _ = Avis.objects.get_or_create(
        lieu=lieu4, user=amine,
        defaults={
            'note': 5,
            'note_qualite': 5,
            'note_service': 5,
            'note_prix': 4,
            'note_ambiance': 5,
            'commentaire': "Magnifique halte paisible au milieu de l'effervescence de la Médina. La malsouka est croustillante et le cadre est tout simplement splendide.",
            'score_confiance': 0.95,
            'type_visiteur': 'RESIDENT'
        }
    )

    # 6. Module Transports (Lignes & Stations de Tunis)
    t_tgm, _ = MoyenTransport.objects.get_or_create(nom="TGM (Tunis - Goulette - Marsa)", defaults={'icone': 'train', 'vitesse_moyenne_kmh': 40.0, 'tarif_base_tnd': 0.9, 'tarif_km_tnd': 0.05, 'confort': 'Moyen', 'ecologique': True, 'description': "La ligne ferroviaire historique qui relie la capitale à la banlieue nord."})
    t_metro, _ = MoyenTransport.objects.get_or_create(nom="Métro Léger de Tunis", defaults={'icone': 'subway', 'vitesse_moyenne_kmh': 25.0, 'tarif_base_tnd': 0.6, 'tarif_km_tnd': 0.04, 'confort': 'Moyen', 'ecologique': True, 'description': "Réseau de tramway moderne desservant le centre et les banlieues."})
    t_taxi, _ = MoyenTransport.objects.get_or_create(nom="Taxi / VTC (Bolt, OTaxi)", defaults={'icone': 'taxi', 'vitesse_moyenne_kmh': 35.0, 'tarif_base_tnd': 1.0, 'tarif_km_tnd': 0.9, 'confort': 'Élevé', 'ecologique': False, 'description': "Taxis jaunes ou VTC avec réservation rapide et climatisée."})
    t_pied, _ = MoyenTransport.objects.get_or_create(nom="À pied", defaults={'icone': 'walking', 'vitesse_moyenne_kmh': 4.5, 'tarif_base_tnd': 0.0, 'tarif_km_tnd': 0.0, 'confort': 'Sain', 'ecologique': True, 'description': "La meilleure façon d'explorer ruelles et paysages."})
    t_voiture, _ = MoyenTransport.objects.get_or_create(nom="Voiture personnelle", defaults={'icone': 'car', 'vitesse_moyenne_kmh': 45.0, 'tarif_base_tnd': 2.5, 'tarif_km_tnd': 0.4, 'confort': 'Élevé', 'ecologique': False, 'description': "Voiture de location ou personnelle avec carburant et péages."})

    # Lignes
    l_tgm, _ = Ligne.objects.get_or_create(nom="Ligne TGM Banlieue Nord", defaults={'code': 'TGM', 'couleur': '#0284c7', 'moyen_transport': t_tgm})
    l_m1, _ = Ligne.objects.get_or_create(nom="Ligne 1 Métro Barcelone - Ben Arous", defaults={'code': 'M1', 'couleur': '#16a34a', 'moyen_transport': t_metro})

    # Stations TGM
    s_marine, _ = Station.objects.get_or_create(nom="Tunis Marine", defaults={'type': 'TGM', 'ligne': l_tgm, 'latitude': 36.8005, 'longitude': 10.1915, 'ordre': 1})
    s_goulette, _ = Station.objects.get_or_create(nom="La Goulette Casino", defaults={'type': 'TGM', 'ligne': l_tgm, 'latitude': 36.8190, 'longitude': 10.3060, 'ordre': 6})
    s_carthage, _ = Station.objects.get_or_create(nom="Carthage Hannibal", defaults={'type': 'TGM', 'ligne': l_tgm, 'latitude': 36.8530, 'longitude': 10.3320, 'ordre': 12})
    s_sidi, _ = Station.objects.get_or_create(nom="Sidi Bou Saïd Station", defaults={'type': 'TGM', 'ligne': l_tgm, 'latitude': 36.8682, 'longitude': 10.3395, 'ordre': 15})
    s_marsa, _ = Station.objects.get_or_create(nom="Marsa Plage (Terminus)", defaults={'type': 'TGM', 'ligne': l_tgm, 'latitude': 36.8795, 'longitude': 10.3275, 'ordre': 18})

    # Liaison Lieux <-> Stations
    LieuStation.objects.get_or_create(lieu=lieu1, station=s_sidi, defaults={'distance_metres': 450, 'temps_marche_minutes': 6})
    LieuStation.objects.get_or_create(lieu=lieu2, station=s_sidi, defaults={'distance_metres': 300, 'temps_marche_minutes': 4})
    LieuStation.objects.get_or_create(lieu=lieu3, station=s_marsa, defaults={'distance_metres': 250, 'temps_marche_minutes': 3})
    LieuStation.objects.get_or_create(lieu=lieu5, station=s_carthage, defaults={'distance_metres': 350, 'temps_marche_minutes': 5})

    # 7. Module Itinéraires
    itin1, _ = Itineraire.objects.get_or_create(
        user=syrine,
        titre="Échappée Bleue & Blanche à Sidi Bou Saïd",
        defaults={
            'description': "Le programme idéal pour une après-midi mémorable : visite du village, pause thé aux nattes, bambalouni croustillant et dîner vue mer à La Marsa.",
            'budget': 55.0,
            'duree_totale': 240,
            'mode_transport': 'MIXTE',
            'est_public': True
        }
    )
    Etape.objects.get_or_create(itineraire=itin1, lieu=lieu2, defaults={'ordre': 1, 'heure_arrivee': '14:30', 'duree_visite': 45, 'mode_transport': 'TGM', 'duree_trajet': 25, 'distance': 15.0, 'notes': "Prendre le TGM jusqu'à Sidi Bou Saïd puis monter à pied aux nattes."})
    Etape.objects.get_or_create(itineraire=itin1, lieu=lieu1, defaults={'ordre': 2, 'heure_arrivee': '15:30', 'duree_visite': 60, 'mode_transport': 'PIED', 'duree_trajet': 10, 'distance': 0.6, 'notes': "Admirer la vue imprenable sur le golfe de Tunis."})
    Etape.objects.get_or_create(itineraire=itin1, lieu=lieu3, defaults={'ordre': 3, 'heure_arrivee': '19:00', 'duree_visite': 120, 'mode_transport': 'TAXI', 'duree_trajet': 10, 'distance': 2.8, 'notes': "Dîner gastronomique au bord de l'eau à La Marsa."})

    # Liste de favoris
    fav_list, _ = ListeFavoris.objects.get_or_create(user=syrine, nom="Mes coups de cœur de Tunis", defaults={'visibilite': 'PUBLIC'})
    fav_list.lieux.add(lieu1, lieu2, lieu4)

    # 8. Module Événements et Bons Plans
    now = timezone.now()
    Evenement.objects.get_or_create(
        lieu=lieu4,
        titre="Nuit Musicale Soufie & Dégustation Patrimoniale",
        defaults={
            'description': "Une soirée magique dans le patio illuminé aux chandelles de Fondouk El Attarine avec chants mystiques et dîner gastronomique traditionnel.",
            'date_debut': now + timedelta(days=3, hours=19),
            'date_fin': now + timedelta(days=3, hours=23),
            'image': 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80',
            'prix': 65.0,
            'categorie': 'Concert & Musique',
            'est_populaire': True
        }
    )

    Evenement.objects.get_or_create(
        lieu=lieu6,
        titre="Sunset Electronic Sessions @ Gammarth",
        defaults={
            'description': "Les meilleurs DJs de la scène tunisienne et internationale se relaient pour un coucher de soleil festif face à la mer.",
            'date_debut': now + timedelta(days=5, hours=17),
            'date_fin': now + timedelta(days=6, hours=2),
            'image': 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80',
            'prix': 30.0,
            'categorie': 'Festival & Fête',
            'est_populaire': True
        }
    )

    # Offres partenaires
    OffrePromotion.objects.get_or_create(
        lieu=lieu3,
        titre="Menu Dégustation -15% Spécial TunisSpot",
        defaults={
            'description': "Profitez de 15% de réduction immédiate sur le menu dégustation midi en présentant l'application TunisSpot.",
            'code_promo': 'TUNISSPOT15',
            'reduction_pourcentage': 15,
            'date_debut': now.date(),
            'date_fin': now.date() + timedelta(days=30),
            'est_active': True
        }
    )

    # Statistiques de fiches
    StatistiqueFiche.objects.get_or_create(
        lieu=lieu1,
        date_stat=now.date(),
        defaults={'nombre_vues': 420, 'nombre_clics_itineraire': 88, 'nombre_ajouts_favoris': 54, 'nombre_clics_menu': 95}
    )
    StatistiqueFiche.objects.get_or_create(
        lieu=lieu3,
        date_stat=now.date(),
        defaults={'nombre_vues': 310, 'nombre_clics_itineraire': 45, 'nombre_ajouts_favoris': 32, 'nombre_clics_menu': 110}
    )

    # Notifications
    Notification.objects.get_or_create(
        user=syrine,
        titre="Nouveau badge débloqué !",
        defaults={
            'message': "Félicitations ! Vous avez débloqué le badge 'Explorateur de la Médina' grâce à vos contributions.",
            'lien': '/users/profil/',
            'est_lue': False
        }
    )

    print("=== Données initialisées avec succès ! ===")

if __name__ == '__main__':
    seed()
