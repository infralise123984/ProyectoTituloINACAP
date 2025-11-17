# pagina/management/commands/cargar_unidades.py
from django.core.management.base import BaseCommand
from pagina.models import Unidad

class Command(BaseCommand):
    help = 'Carga unidades iniciales en la base de datos'

    def handle(self, *args, **options):
        unidades = [
            ("HRFRZ - Urgencia Adulto", "HRFRZ"),
            ("HRFRZ - Traumatología Infantil", "HRFRZ-PED"),
            ("Telered Urgencias O’Higgins", "TELERED"),
            ("Código IAM", "IAM"),
            ("RIUE - Área Norte", "RIUE"),
            ("Ambulancia RIU", "RIU"),
            ("SAR Oriente", "SAR-ORIENTE"),
            ("Urgencia Carretera de la Fruta", "CARRETERA"),
            ("Red Integrada Santa Cruz", "SANTA-CRUZ"),
            ("Telered San Fernando Adulto", "TEL-SF-AD"),
            ("Telered San Fernando Pediatría", "TEL-SF-PED"),
            ("Red Cachapoal SUR", "CACHA-SUR"),
        ]

        for nombre, codigo in unidades:
            obj, created = Unidad.objects.get_or_create(
                nombre=nombre,
                defaults={'codigo': codigo}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✓ {nombre}"))
            else:
                self.stdout.write(self.style.WARNING(f"Ya existe: {nombre}"))

        self.stdout.write(self.style.SUCCESS("¡Unidades cargadas!"))