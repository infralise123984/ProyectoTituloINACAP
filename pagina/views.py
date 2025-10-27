# pagina/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Anamnesis, PerfilUsuario
from .forms import RegistroForm  # ← NUEVA IMPORTACIÓN

def index(request):
    if request.user.is_authenticated:
        return redirect('enviar')
    return render(request, 'index.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('enviar')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('enviar')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def registro(request):
    if request.user.is_authenticated:
        return redirect('enviar')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            especialidad = form.cleaned_data.get('especialidad')
            PerfilUsuario.objects.create(user=user, especialidad=especialidad)
            login(request, user)
            return redirect('enviar')
    else:
        form = RegistroForm()

    return render(request, 'registro.html', {'form': form})


@login_required
def enviar(request):
    if request.method == 'POST':
        Anamnesis.objects.create(
            nombre_paciente=request.POST['nombre_paciente'],
            apellido_paciente=request.POST['apellido_paciente'],
            motivo=request.POST['motivo'],
            sintomas=request.POST['sintomas'],
            # antecedentes y unidad_destino no están en modelo → ignoramos
            usuario=request.user
        )
        return redirect('buscar')
    return render(request, 'enviar.html')
@login_required
def buscar(request):
    # Obtener perfil del usuario
    try:
        perfil = request.user.perfil
    except PerfilUsuario.DoesNotExist:
        # Si no tiene perfil, crear uno vacío (opcional)
        perfil = PerfilUsuario.objects.create(user=request.user)

    # Definir si es "doctor" (puedes cambiar el nombre)
    es_doctor = perfil.especialidad and perfil.especialidad.nombre.lower() in ['médico', 'medico', 'doctor']

    if es_doctor:
        # Doctores ven TODAS las anamnesis
        anamnesis = Anamnesis.objects.all().order_by('-fecha_envio')
    else:
        # Paramédicos solo ven las suyas
        anamnesis = Anamnesis.objects.filter(usuario=request.user).order_by('-fecha_envio')

    return render(request, 'buscar.html', {'anamnesis': anamnesis})
@login_required
def logout_view(request):
    logout(request)
    return redirect('index')