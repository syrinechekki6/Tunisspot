from django import forms
from .models import Lieu, Plat, Avis, Photo, Revendication, Signalement

class LieuForm(forms.ModelForm):
    image_principale = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'placeholder': 'https://images.unsplash.com/... (URL de la photo, optionnelle)'})
    )

    def clean_image_principale(self):
        val = self.cleaned_data.get('image_principale')
        if not val or not val.strip():
            return 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80'
        return val.strip()

    class Meta:
        model = Lieu
        fields = [
            'nom', 'categorie', 'quartier', 'adresse', 'latitude', 'longitude',
            'telephone', 'site_web', 'fourchette_prix', 'prix_moyen', 'horaires',
            'description', 'image_principale', 'wifi', 'terrasse', 'parking',
            'acces_pmr', 'vue_mer', 'climatisation', 'ambiance_romantique',
            'ambiance_famille', 'ambiance_amis', 'halal', 'vegetarien'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:border-teal-500 focus:outline-none'}),
            'categorie': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:border-teal-500 focus:outline-none'}),
            'quartier': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:border-teal-500 focus:outline-none'}),
            'adresse': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:border-teal-500 focus:outline-none'}),
            'latitude': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'step': '0.0001'}),
            'longitude': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'step': '0.0001'}),
            'telephone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'site_web': forms.URLInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'fourchette_prix': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'prix_moyen': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'horaires': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'rows': 4}),
            'image_principale': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
        }

class PlatForm(forms.ModelForm):
    class Meta:
        model = Plat
        fields = ['nom', 'categorie_plat', 'prix', 'description', 'photo', 'est_populaire']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'categorie_plat': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'prix': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'step': '0.5', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'rows': 3}),
            'photo': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'placeholder': 'https://images.unsplash.com/... (URL photo du plat)'}),
            'est_populaire': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-amber-500 rounded border-slate-300 focus:ring-amber-400'}),
        }

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['url', 'legende']
        widgets = {
            'url': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'placeholder': 'https://images.unsplash.com/... (URL de la photo)'}),
            'legende': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'placeholder': 'Ex: Ambiance en terrasse, vue sur mer...'}),
        }

class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['note', 'note_qualite', 'note_service', 'note_prix', 'note_ambiance', 'commentaire']
        widgets = {
            'note': forms.Select(choices=[(i, f"{i} étoiles") for i in range(1, 6)], attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl font-bold'}),
            'note_qualite': forms.Select(choices=[(i, f"{i} / 5") for i in range(1, 6)], attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'note_service': forms.Select(choices=[(i, f"{i} / 5") for i in range(1, 6)], attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'note_prix': forms.Select(choices=[(i, f"{i} / 5") for i in range(1, 6)], attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'note_ambiance': forms.Select(choices=[(i, f"{i} / 5") for i in range(1, 6)], attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'commentaire': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'rows': 4, 'placeholder': 'Racontez votre expérience, les plats testés, l\'ambiance...'}),
        }

class RevendicationForm(forms.ModelForm):
    class Meta:
        model = Revendication
        fields = ['justificatif', 'telephone_contact']
        widgets = {
            'justificatif': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'rows': 4, 'placeholder': 'Indiquez votre fonction, le lien avec l\'établissement ou matricule fiscal...'}),
            'telephone_contact': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'placeholder': '+216 ...'}),
        }

class SignalementForm(forms.ModelForm):
    class Meta:
        model = Signalement
        fields = ['motif', 'description']
        widgets = {
            'motif': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl font-semibold'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'rows': 4, 'placeholder': 'Expliquez en détail le problème rencontré...'}),
        }
