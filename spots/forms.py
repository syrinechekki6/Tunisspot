from django import forms
from .models import Lieu, Revendication, Signalement

class LieuForm(forms.ModelForm):
    image_principale = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'placeholder': 'https://images.unsplash.com/...'})
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
            'nom': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'categorie': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'quartier': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'adresse': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'latitude': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'step': '0.0001'}),
            'longitude': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'step': '0.0001'}),
            'telephone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'site_web': forms.URLInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'fourchette_prix': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'prix_moyen': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'horaires': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'rows': 4}),
        }

class RevendicationForm(forms.ModelForm):
    class Meta:
        model = Revendication
        fields = ['justificatif', 'telephone_contact']
        widgets = {
            'justificatif': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'rows': 4}),
            'telephone_contact': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
        }

class SignalementForm(forms.ModelForm):
    class Meta:
        model = Signalement
        fields = ['motif', 'description']
        widgets = {
            'motif': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'rows': 3}),
        }
