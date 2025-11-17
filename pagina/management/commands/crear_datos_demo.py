# pagina/management/commands/crear_datos_demo.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pagina.models import Unidad, PerfilUsuario, Anamnesis
from django.utils import timezone
from django.conf import settings
import random
import os


class Command(BaseCommand):
    help = "Crea datos demo para showcase: 14 usuarios + 12 anamnesis + credenciales_demo.txt"

    def handle(self, *args, **kwargs):
        # ======================================================
        # 1. CREAR LAS DOS UNIDADES DEL DEMO
        # ======================================================
        hrfrz, _ = Unidad.objects.get_or_create(
            nombre="HRFRZ - Urgencia Adulto",
            defaults={"codigo": "HRFRZ"}
        )
        riue, _ = Unidad.objects.get_or_create(
            nombre="RIUE - Área Norte",
            defaults={"codigo": "RIUE"}
        )
        unidades = [hrfrz, riue]

        # ======================================================
        # 2. CREAR 2 USUARIOS POR CADA ROL (14 en total)
        # ======================================================
        roles = [
            "paramedico", "tens", "enfermero", "medico",
            "coordinador", "ambulancia", "admin_red"
        ]

        credenciales = [
            "=== CREDENCIALES DEMO - INTERÁREA ===\n\n",
            f"Generado: {timezone.localtime().strftime('%d/%m/%Y %H:%M')}\n\n",
            "USUARIO         CONTRASEÑA    ROL                         UNIDAD\n",
            "-" * 80 + "\n"
        ]

        for rol in roles:
            rol_display = dict(PerfilUsuario.ROLES).get(rol, rol.replace("_", " ").title())
            for i in range(1, 3):
                username = f"{rol}{i}"
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={"first_name": f"{rol_display} {i}", "last_name": "Demo"}
                )
                if created:
                    user.set_password("demo123")
                    user.save()

                # Mitad en HRFRZ, mitad en RIUE
                unidad = hrfrz if (i == 1) else riue
                PerfilUsuario.objects.update_or_create(
                    user=user,
                    defaults={"rol": rol, "unidad": unidad}
                )

                credenciales.append(
                    f"{username:<15} demo123      {rol_display:<27} {unidad.nombre}\n"
                )

        # ======================================================
        # 3. OBTENER EMISORES (CORREGIDO: sin usar property)
        # ======================================================
        emisores = User.objects.filter(
            perfil__rol__in=['paramedico', 'tens', 'ambulancia']
        ).distinct()

        if not emisores.exists():
            self.stdout.write(self.style.ERROR("No se encontraron emisores. Revisa los roles."))
            return

        # ======================================================
        # 4. DATOS CLÍNICOS POR GRAVEDAD
        # ======================================================
        alto = [
            ("Paro cardiorrespiratorio", "Sin pulso ni respiración", "inconsciente", 0, "0/0", 0, 36.0),
            ("Shock séptico grave", "Hipotensión + fiebre alta", "verbal", 145, "75/40", 32, 39.9),
            ("TCE grave", "Pupilas fijas, GCS 4", "inconsciente", 50, "180/110", 8, 35.2),
            ("IAM con edema pulmonar", "Dolor intenso + disnea", "dolor", 155, "90/50", 30, 37.5),
        ]
        medio = [
            ("Descompensación EPOC", "Disnea severa", "alerta", 115, "150/95", 28, 38.0),
            ("Cetoacidosis diabética", "Polipnea + confusión", "verbal", 130, "100/60", 32, 37.8),
            ("Neumonía grave", "Fiebre + hipoxemia", "alerta", 120, "140/90", 26, 39.0),
            ("Dolor torácico atípico", "Sospecha de SCA", "alerta", 105, "130/85", 22, 37.2),
        ]
        bajo = [
            ("Esguince de tobillo", "Dolor leve", "alerta", 78, "120/80", 16, 36.6),
            ("Cefalea tensional", "Sin signos de alarma", "alerta", 82, "125/78", 14, 36.5),
            ("Herida superficial", "Sangrado controlado", "alerta", 80, "118/76", 16, 36.7),
            ("Gastroenteritis", "Vómitos tolerados", "alerta", 88, "115/75", 18, 36.8),
        ]

        # ======================================================
        # 5. CREAR LAS 12 ANAMNESIS
        # ======================================================
        combinaciones = [(alto, 4), (medio, 4), (bajo, 4)]
        contador = 0

        for datos, cantidad in combinaciones:
            for _ in range(cantidad):
                unidad_destino = unidades[contador % 2]
                emisor = random.choice(emisores)
                motivo, sintomas, conciencia, fc, pa, fr, temp = random.choice(datos)

                a = Anamnesis(
                    usuario=emisor,
                    unidad_destino=unidad_destino,
                    nombre_paciente=random.choice(["Juan", "María", "Pedro", "Ana", "Luis", "NN"]),
                    apellido_paciente=random.choice(["Pérez", "Gómez", "Rojas", "Silva", "Díaz", ""]),
                    rut_paciente=random.choice(["", "12.345.678-9", "18.765.432-1"]),
                    motivo=motivo,
                    sintomas=sintomas,
                    antecedentes=random.choice([
                        "HTA", "DM2", "EPOC", "Sin antecedentes", "Alergia a penicilina"
                    ]),
                    nivel_conciencia=conciencia,
                    frecuencia_cardiaca=fc if fc > 0 else None,
                    presion_arterial=pa,
                    frecuencia_respiratoria=fr if fr > 0 else None,
                    temperatura=temp,
                    estado=random.choice(["enviada", "enviada", "aceptada"]),
                )
                a.fecha_envio = timezone.now() - timezone.timedelta(minutes=random.randint(10, 600))
                a.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"→ Anamnesis #{a.id} | GRAVEDAD: {a.get_gravedad_display().upper()} | "
                        f"{emisor.username} → {unidad_destino.nombre}"
                    )
                )
                contador += 1

        # ======================================================
        # 6. GUARDAR CREDENCIALES
        # ======================================================
        ruta = os.path.join(settings.BASE_DIR, "credenciales_demo.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.writelines(credenciales)

        self.stdout.write(self.style.SUCCESS(
            f"\n¡SHOWCASE LISTO EN {contador} ANAMNESIS!\n"
            f"→ 14 usuarios creados (usuario: cualquiera | contraseña: demo123)\n"
            f"→ 12 anamnesis clínicas reales con gravedad correcta\n"
            f"→ Archivo de credenciales creado: {ruta}\n"
            f"\n¡AHORA SÍ, VAS A ROMPERLA EN TU DEFENSA!"
        ))