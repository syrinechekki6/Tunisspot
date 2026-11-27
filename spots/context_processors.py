from spots.models import Categorie, Quartier
from users.models import Notification

def tunisspot_context(request):
    categories = Categorie.objects.all()
    quartiers = Quartier.objects.all()
    notifs_unread_count = 0
    if request.user.is_authenticated:
        notifs_unread_count = Notification.objects.filter(user=request.user, est_lue=False).count()
    return {
        'nav_categories': categories,
        'nav_quartiers': quartiers,
        'notifs_unread_count': notifs_unread_count,
        'app_name': 'TunisSpot',
        'tagline': 'Découvre les meilleurs spots et bons plans à Tunis',
        'tagline_ar': 'وين تخرج في تونس - أفضل الأماكن والأنشطة',
    }
