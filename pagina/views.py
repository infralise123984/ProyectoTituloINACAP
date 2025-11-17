# pagina/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.utils import timezone
from datetime import date
from .models import Anamnesis, PerfilUsuario
from .forms import RegistroForm, AnamnesisForm

@login_required
def hud(request):
    try:
        perfil = request.user.perfil
    except PerfilUsuario.DoesNotExist:
        return render(request, 'error_perfil.html', {'mensaje': 'Perfil no configurado.'})

    # KPIs que siempre funcionan
    pendientes_global   = Anamnesis.objects.filter(estado='enviada').count()
    altas_gravedad      = Anamnesis.objects.filter(gravedad='alto').count()

    if perfil.es_emisor:
        total_enviadas = Anamnesis.objects.filter(usuario=request.user).count()
    else:
        total_enviadas = None  # no lo necesitamos en hospital

    # Últimas 5 (igual que antes, pero sin filtro de fecha)
    if perfil.es_emisor:
        ultimas = Anamnesis.objects.filter(usuario=request.user).order_by('-fecha_envio')[:4]
    else:
        ultimas = Anamnesis.objects.filter(unidad_destino=perfil.unidad).order_by('-fecha_envio')[:4]

    context = {
        'pendientes': pendientes_global,
        'altas_gravedad': altas_gravedad,
        'total_enviadas': total_enviadas,
        'ultimas': ultimas,
        'now': timezone.localtime(),
    }
    return render(request, 'hud.html', context)
# === DECORADOR PARA ADMIN_RED ===
def requires_admin_red(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            if request.user.perfil.rol == "admin_red":
                return view_func(request, *args, **kwargs)
        except:
            pass
        return HttpResponseForbidden("Acceso denegado.")

    return wrapper


def index(request):
    if request.user.is_authenticated:
        return redirect("/hud/")
    return render(request, "index.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/hud/")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("/hud/")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


@requires_admin_red
def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/hud/")
    else:
        form = RegistroForm()
    return render(request, "registro.html", {"form": form})


@login_required
def enviar(request):
    try:
        request.user.perfil
    except PerfilUsuario.DoesNotExist:
        return render(
            request, "error_perfil.html", {"mensaje": "Perfil no configurado."}
        )

    if request.method == "POST":
        form = AnamnesisForm(request.POST)
        if form.is_valid():
            anamnesis = form.save(commit=False)
            anamnesis.usuario = request.user
            anamnesis.save()
            return redirect("/hud/")
    else:
        form = AnamnesisForm()
    return render(request, "enviar.html", {"form": form})


@login_required
def buscar(request):
    try:
        perfil = request.user.perfil
    except PerfilUsuario.DoesNotExist:
        return render(
            request, "error_perfil.html", {"mensaje": "Perfil no configurado."}
        )

    if not perfil.unidad:
        return render(
            request, "error_perfil.html", {"mensaje": "No tienes unidad asignada."}
        )

    if perfil.es_receptor:
        anamnesis = Anamnesis.objects.filter(unidad_destino=perfil.unidad).order_by(
            "-fecha_envio"
        )
    else:
        anamnesis = Anamnesis.objects.filter(usuario=request.user).order_by(
            "-fecha_envio"
        )
    context = {
        "anamnesis": anamnesis,
        "estados": Anamnesis.ESTADOS,      # para el filtro de estado
        "gravedades": Anamnesis.GRAVEDAD,  # para el filtro de gravedad
    }
    return render(request, "buscar.html", context)


# === ACEPTAR ANAMNESIS (solo médico y enfermero) ===
@login_required
def aceptar_anamnesis(request, pk):
    anamnesis = get_object_or_404(Anamnesis, pk=pk)

    # Solo médico o enfermero pueden aceptar
    if request.user.perfil.rol not in ["medico", "enfermero"]:
        return HttpResponseForbidden(
            "Solo médicos y enfermeros pueden aceptar anamnesis."
        )

    # Opcional: verificar que sea de su unidad
    if anamnesis.unidad_destino != request.user.perfil.unidad:
        return HttpResponseForbidden("No puedes aceptar anamnesis de otra unidad.")

    anamnesis.estado = "aceptada"
    anamnesis.save()

    return redirect("buscar")


@login_required
def logout_view(request):
    logout(request)
    return redirect("index")
