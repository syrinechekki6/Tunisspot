from spots.models import Categorie, Quartier

def tunisspot_context(request):
    categories = Categorie.objects.all()
    quartiers = Quartier.objects.all()
    return {
        "nav_categories": categories,
        "nav_quartiers": quartiers,
        "app_name": "TunisSpot - Avis & Menus",
        "tagline": "Gestion des avis, photos et menus a Tunis",
    }
