from django import forms
from .models import Itineraire, Etape, ListeFavoris, SortieGroupe, PropositionLieu

class ItineraireForm(forms.ModelForm):
    class Meta:
        model = Itineraire
        fields = ['titre', 'description', 'budget', 'duree_totale', 'mode_transport', 'est_public']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'rows': 3}),
            'budget': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'duree_totale': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'mode_transport': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
        }

class EtapeForm(forms.ModelForm):
    class Meta:
        model = Etape
        fields = ['lieu', 'ordre', 'heure_arrivee', 'duree_visite', 'mode_transport', 'duree_trajet', 'distance', 'notes']
        widgets = {
            'lieu': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'ordre': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'heure_arrivee': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'duree_visite': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'mode_transport': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'duree_trajet': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'distance': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'notes': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
        }

class ListeFavorisForm(forms.ModelForm):
    class Meta:
        model = ListeFavoris
        fields = ['nom', 'visibilite']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'visibilite': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
        }

class SortieGroupeForm(forms.ModelForm):
    class Meta:
        model = SortieGroupe
        fields = ['titre', 'date_sortie', 'description']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'placeholder': 'Ex: Sortie samedi à La Marsa'}),
            'date_sortie': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'rows': 3}),
        }
