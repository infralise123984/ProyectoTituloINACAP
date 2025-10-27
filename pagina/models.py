from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# === ESPECIALIDAD ===
class Especialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"

    def __str__(self):
        return self.nombre


# === PERFIL DE USUARIO (extiende User con especialidad) ===
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    especialidad = models.ForeignKey(
        Especialidad, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.especialidad or 'Sin especialidad'})"


# === ANAMNESIS (mínima, sin RUT validado ni centro) ===
class Anamnesis(models.Model):
    nombre_paciente = models.CharField("Nombre del paciente", max_length=100)
    apellido_paciente = models.CharField("Apellido del paciente", max_length=100)
    motivo = models.TextField("Motivo de consulta")
    sintomas = models.TextField("Síntomas")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='anamnesis')
    fecha_envio = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Anamnesis"
        verbose_name_plural = "Anamnesis"
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"{self.nombre_paciente} {self.apellido_paciente} - {self.motivo[:30]}..."