from django import forms
from .models import Evenement, OffrePromotion, Partenaire

class EvenementForm(forms.ModelForm):
    date_debut = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local', 'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}
        ),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M']
    )
    date_fin = forms.DateTimeField(
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local', 'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}
        ),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M']
    )
    est_populaire = forms.BooleanField(
        required=False,
        initial=True,
        label="Mettre en avant cet événement"
    )

    class Meta:
        model = Evenement
        fields = ['lieu', 'titre', 'description', 'date_debut', 'date_fin', 'image', 'prix', 'categorie', 'est_populaire']
        widgets = {
            'lieu': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'titre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'placeholder': 'Ex: Soirée Acoustique & Jazz'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'rows': 4, 'placeholder': 'Détails de l\'événement...'}),
            'image': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'prix': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'step': 'any', 'min': '0'}),
            'categorie': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'est_populaire': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-rose-500 rounded border-slate-300 focus:ring-rose-400'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            from django.utils import timezone
            now = timezone.now()
            if not self.initial.get('date_debut'):
                self.initial['date_debut'] = (now + timezone.timedelta(days=1)).strftime('%Y-%m-%dT19:00')
            if not self.initial.get('date_fin'):
                self.initial['date_fin'] = (now + timezone.timedelta(days=1, hours=4)).strftime('%Y-%m-%dT23:00')

class OffrePromotionForm(forms.ModelForm):
    date_debut = forms.DateField(
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'date', 'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}
        ),
        input_formats=['%Y-%m-%d', '%d/%m/%Y']
    )
    date_fin = forms.DateField(
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'date', 'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}
        ),
        input_formats=['%Y-%m-%d', '%d/%m/%Y']
    )
    est_active = forms.BooleanField(
        required=False,
        initial=True,
        label="Activer immédiatement cette offre"
    )

    class Meta:
        model = OffrePromotion
        fields = ['lieu', 'titre', 'description', 'code_promo', 'reduction_pourcentage', 'date_debut', 'date_fin', 'est_active']
        widgets = {
            'lieu': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'titre': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'rows': 3}),
            'code_promo': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'placeholder': 'Ex: TUNISSPOT10'}),
            'reduction_pourcentage': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'min': '1', 'max': '100'}),
            'est_active': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-amber-500 rounded border-slate-300 focus:ring-amber-400'}),
        }
