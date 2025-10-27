# tu_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Especialidad


class RegistroForm(UserCreationForm):
    especialidad = forms.ModelChoiceField(
        queryset=Especialidad.objects.all().order_by('nombre'),
        empty_label="Sin especialidad (opcional)",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Especialidad"
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'especialidad')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = 'Mínimo 8 caracteres, no puede ser solo números.'
        self.fields['username'].help_text = None  # Elimina help_text por defecto