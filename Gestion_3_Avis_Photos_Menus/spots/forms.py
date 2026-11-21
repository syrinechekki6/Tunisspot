from django import forms
from .models import Avis, Photo, Plat

class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['note', 'commentaire']
        widgets = {
            'note': forms.Select(choices=[(i, f"{i}/5") for i in range(1, 6)], attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'commentaire': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'rows': 4}),
        }

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['url', 'legende']
        widgets = {
            'url': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'placeholder': 'https://images.unsplash.com/...'}),
            'legende': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
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
            'photo': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'est_populaire': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-amber-500 rounded border-slate-300'}),
        }
