# pagina/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario, Anamnesis, Unidad


# === FORMULARIO DE REGISTRO (solo admin) ===
class RegistroForm(UserCreationForm):
    rol = forms.ChoiceField(
        choices=PerfilUsuario.ROLES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Rol"
    )
    unidad = forms.ModelChoiceField(
        queryset=Unidad.objects.all().order_by('nombre'),
        empty_label="Seleccionar unidad",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Unidad de Salud"
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'rol', 'unidad')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            PerfilUsuario.objects.create(
                user=user,
                rol=self.cleaned_data['rol'],
                unidad=self.cleaned_data['unidad']
            )
        return user





# === FORMULARIO DE ENVÍO DE ANAMNESIS ===
class AnamnesisForm(forms.ModelForm):
    class Meta:
        model = Anamnesis
        exclude = ['usuario', 'estado', 'fecha_envio', 'gravedad']
        widgets = {
            'nombre_paciente': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Nombre'}),
            'apellido_paciente': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Apellido'}),
            'rut_paciente': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'RUT'}),
            'motivo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control form-control-lg'}),
            'sintomas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control form-control-lg'}),
            'antecedentes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control form-control-lg'}),
            'nivel_conciencia': forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'frecuencia_cardiaca': forms.NumberInput(attrs={'class': 'form-control form-control-lg'}),
            'presion_arterial': forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
            'frecuencia_respiratoria': forms.NumberInput(attrs={'class': 'form-control form-control-lg'}),
            'temperatura': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control form-control-lg'}),
            'unidad_destino': forms.Select(attrs={'class': 'form-select form-select-lg'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # === Paciente: OPCIONAL ===
        self.fields['nombre_paciente'].required = False
        self.fields['apellido_paciente'].required = False
        self.fields['rut_paciente'].required = False
        self.fields['nombre_paciente'].initial = ''
        self.fields['apellido_paciente'].initial = ''
        self.fields['rut_paciente'].initial = ''

        # === OBLIGATORIOS (pero con valor por defecto aceptable) ===
        self.fields['motivo'].required = True
        self.fields['sintomas'].required = True
        self.fields['antecedentes'].required = True
        self.fields['unidad_destino'].required = True

        # === Signos vitales: OBLIGATORIOS, pero con opción "no se sabe" ===
        self.fields['nivel_conciencia'].required = True
        self.fields['frecuencia_cardiaca'].required = True
        self.fields['presion_arterial'].required = True
        self.fields['frecuencia_respiratoria'].required = True
        self.fields['temperatura'].required = True

        # Añadir opción "No evaluado" al select
        self.fields['nivel_conciencia'].choices = [
            ('', '--- Seleccionar ---'),
            ('no_evaluado', 'No evaluado'),
            ('alerta', 'Alerta'),
            ('verbal', 'Responde a voz'),
            ('dolor', 'Responde a dolor'),
            ('inconsciente', 'Inconsciente'),
        ]

        # Placeholder para números
        self.fields['frecuencia_cardiaca'].widget.attrs['placeholder'] = 'Ej: 80'
        self.fields['frecuencia_respiratoria'].widget.attrs['placeholder'] = 'Ej: 16'
        self.fields['temperatura'].widget.attrs['placeholder'] = 'Ej: 36.6'
        self.fields['presion_arterial'].widget.attrs['placeholder'] = 'Ej: 120/80'

# === FORMULARIO DE LOGIN (opcional, más limpio) ===
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))