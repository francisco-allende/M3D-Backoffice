# m3d_app/management/commands/corregir_bloques.py

from django.core.management.base import BaseCommand
from django.db.models import Q
from m3d_app.models.bloque3d.bloque import Bloque

class Command(BaseCommand):
    help = 'Corrige los estados de bloques sin suscriptor, estableciéndolos como "libre"'

    def handle(self, *args, **options):
        # Encontrar bloques con estados incompatibles
        bloques_a_corregir = Bloque.objects.filter(
            ~Q(estado='libre'), 
            suscriptor__isnull=True
        )
        
        count = bloques_a_corregir.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("No hay bloques que necesiten corrección"))
            return
            
        self.stdout.write(self.style.WARNING(f"Se encontraron {count} bloques con estado incorrecto (sin suscriptor)"))
        
        # Mostrar los bloques a corregir
        for bloque in bloques_a_corregir:
            self.stdout.write(f"  - Bloque {bloque.numero_bloque} con estado '{bloque.estado}'")
        
        # Confirmar antes de proceder
        if input("¿Deseas corregir estos bloques? (s/n): ").lower() != 's':
            self.stdout.write(self.style.WARNING("Operación cancelada"))
            return
        
        # Actualizar a estado 'libre'
        bloques_a_corregir.update(
            estado='libre',
            fecha_asignacion=None,
            fecha_validacion=None,
            fecha_entrega_nodo=None,
            fecha_recepcion_m3d=None,
            fecha_entrega_diploma=None
        )
        
        self.stdout.write(self.style.SUCCESS(f"Se han corregido {count} bloques. Todos tienen ahora estado 'libre'"))