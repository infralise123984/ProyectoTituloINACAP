# pagina/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


# === UNIDAD DE SALUD (Red O'Higgins - ESCALABLE) ===
class Unidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=20, unique=True, blank=True, help_text="Ej: HRFRZ, RIUE")

    class Meta:
        verbose_name = "Unidad de Salud"
        verbose_name_plural = "Unidades de Salud"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


# === PERFIL DE USUARIO (sin Especialidad) ===
class PerfilUsuario(models.Model):
    ROLES = [
        ('paramedico', 'Paramédico'),
        ('tens', 'TENS'),
        ('enfermero', 'Enfermero/a'),
        ('medico', 'Médico/Doctor'),
        ('coordinador', 'Coordinador Telered/Unidad'),
        ('ambulancia', 'Personal Ambulancia RIU/SAR'),
        ('admin_red', 'Administrador Red/SSO'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default='paramedico')
    unidad = models.ForeignKey(Unidad, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"

    @property
    def es_receptor(self):
        return self.rol in ['medico', 'tens', 'enfermero', 'coordinador']

    @property
    def es_emisor(self):
        return self.rol in ['paramedico', 'tens', 'ambulancia']


# === ANAMNESIS (minimalista, móvil) ===
class Anamnesis(models.Model):
    # --- Paciente ---
    nombre_paciente = models.CharField("Nombre", max_length=100, default='NN')
    apellido_paciente = models.CharField("Apellido", max_length=100, blank=True)
    rut_paciente = models.CharField("RUT", max_length=12, blank=True, help_text="Ej: 12.345.678-9", default='NN')

    # --- Clínica ---
    motivo = models.TextField("Motivo de consulta")
    sintomas = models.TextField("Síntomas")
    antecedentes = models.TextField("Antecedentes", blank=True)

    # --- Evaluación de Gravedad (AVPU + vitales) ---
    nivel_conciencia = models.CharField(
        "Nivel de conciencia (AVPU)",
        max_length=20,
        choices=[
            ('alerta', 'Alerta'),
            ('verbal', 'Responde a voz'),
            ('dolor', 'Responde a dolor'),
            ('inconsciente', 'Inconsciente'),
        ],
        blank=True
    )
    frecuencia_cardiaca = models.IntegerField(
        "Frec. Cardíaca (lpm)", null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(300)]
    )
    presion_arterial = models.CharField("Presión Arterial", max_length=20, blank=True)
    frecuencia_respiratoria = models.IntegerField(
        "Frec. Respiratoria (rpm)", null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    temperatura = models.DecimalField(
        "Temperatura (°C)", max_digits=4, decimal_places=1,
        null=True, blank=True,
        validators=[MinValueValidator(25), MaxValueValidator(45)]
    )

    # --- Logística ---
    unidad_destino = models.ForeignKey(
        Unidad, on_delete=models.SET_NULL, null=True,
        related_name='anamnesis_recibidas'
    )

    # --- Estado y tiempos ---
    ESTADOS = [
        ('enviada', 'Enviada'),
        ('recibida', 'Recibida'),
        ('aceptada', 'Aceptada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='enviada')
    fecha_envio = models.DateTimeField(default=timezone.now)  # HORA CHILE
    

    # --- Usuario ---
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='anamnesis')

    # --- Gravedad calculada ---
    GRAVEDAD = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
    ]
    gravedad = models.CharField(max_length=10, choices=GRAVEDAD, default='bajo')

    class Meta:
        verbose_name = "Anamnesis"
        verbose_name_plural = "Anamnesis"
        ordering = ['-fecha_envio']

    def __str__(self):
        paciente = f"{self.nombre_paciente} {self.apellido_paciente}".strip()
        if paciente == 'NN': paciente = 'NN (No identificado)'
        return f"{paciente} → {self.unidad_destino} [{self.get_gravedad_display()}]"

    def save(self, *args, **kwargs):
        # === CÁLCULO AUTOMÁTICO DE GRAVEDAD (NEWS simplificado) ===
        score = 0

        # AVPU
        if self.nivel_conciencia == 'inconsciente': score += 3
        elif self.nivel_conciencia == 'dolor': score += 2
        elif self.nivel_conciencia == 'verbal': score += 1

        # FC
        if self.frecuencia_cardiaca:
            if self.frecuencia_cardiaca <= 40 or self.frecuencia_cardiaca >= 131: score += 3
            elif 41 <= self.frecuencia_cardiaca <= 50 or 111 <= self.frecuencia_cardiaca <= 130: score += 2
            elif 51 <= self.frecuencia_cardiaca <= 90: score += 0
            else: score += 1

        # FR
        if self.frecuencia_respiratoria:
            if self.frecuencia_respiratoria <= 8 or self.frecuencia_respiratoria >= 25: score += 3
            elif 9 <= self.frecuencia_respiratoria <= 11 or 21 <= self.frecuencia_respiratoria <= 24: score += 2
            elif 12 <= self.frecuencia_respiratoria <= 20: score += 0
            else: score += 1

        # Temperatura
        if self.temperatura:
            if self.temperatura <= 35.0 or self.temperatura >= 39.1: score += 3
            elif 35.1 <= self.temperatura <= 36.0 or 38.1 <= self.temperatura <= 39.0: score += 1

        # Asignar gravedad
        if score >= 7:
            self.gravedad = 'alto'
        elif score >= 5:
            self.gravedad = 'medio'
        else:
            self.gravedad = 'bajo'

        super().save(*args, **kwargs)