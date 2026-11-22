import os
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Utilisateur, Preference

def validate_photo_file(photo):
    if not photo:
        return photo
    # Max size 2 Mo (2 * 1024 * 1024 octets)
    max_size = 2 * 1024 * 1024
    if photo.size > max_size:
        raise forms.ValidationError("La taille de l'image ne doit pas dépasser 2 Mo.")
    # Extension validation
    ext = os.path.splitext(photo.name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
        raise forms.ValidationError("Format d'image non supporté. Veuillez utiliser un fichier JPG, PNG ou WEBP.")
    return photo

class InscriptionForm(UserCreationForm):
    INSCRIPTION_ROLE_CHOICES = (
        ('VISITEUR', 'Visiteur (Découverte, Avis, Favoris)'),
        ('PROPRIETAIRE', 'Établissement (Gestionnaire de lieu & Menu)'),
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:border-teal-500',
            'autocomplete': 'off',
            'placeholder': 'exemple@email.com'
        })
    )
    role = forms.ChoiceField(
        choices=INSCRIPTION_ROLE_CHOICES,
        initial='VISITEUR',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:border-teal-500',
            'autocomplete': 'off'
        })
    )
    nom = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:border-teal-500',
            'placeholder': 'Votre nom complet',
            'autocomplete': 'off'
        })
    )
    photo_profil = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-bold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100',
            'accept': '.jpg,.jpeg,.png,.webp'
        })
    )

    class Meta:
        model = Utilisateur
        fields = ['username', 'nom', 'email', 'role', 'langue', 'photo_profil']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:border-teal-500',
                'autocomplete': 'off',
                'placeholder': 'Identifiant unique'
            }),
            'langue': forms.Select(attrs={
                'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:border-teal-500',
                'autocomplete': 'off'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({
                'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:border-teal-500',
                'autocomplete': 'new-password',
                'placeholder': '••••••••'
            })
            self.fields['password1'].help_text = ''
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({
                'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:border-teal-500',
                'autocomplete': 'new-password',
                'placeholder': '••••••••'
            })
            self.fields['password2'].help_text = ''

    def clean_photo_profil(self):
        return validate_photo_file(self.cleaned_data.get('photo_profil'))


class ProfilUpdateForm(forms.ModelForm):
    photo_profil = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-bold file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100',
            'accept': '.jpg,.jpeg,.png,.webp'
        })
    )

    class Meta:
        model = Utilisateur
        fields = ['nom', 'email', 'telephone', 'langue', 'photo_profil']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'telephone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'langue': forms.Select(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
        }

    def clean_photo_profil(self):
        return validate_photo_file(self.cleaned_data.get('photo_profil'))


class PreferenceForm(forms.ModelForm):
    class Meta:
        model = Preference
        fields = ['budget_max', 'ambiances', 'regimes']
        widgets = {
            'budget_max': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl'}),
            'ambiances': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'placeholder': 'romantique,terrasse,calme,vue_mer'}),
            'regimes': forms.TextInput(attrs={'class': 'w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl', 'placeholder': 'halal,vegetarien'}),
        }
