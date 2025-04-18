# En m3d_app/management/commands/revisar_estados_bloques.py

from django.core.management.base import BaseCommand
import pandas as pd
from m3d_app.models.bloque3d.bloque import Bloque
from m3d_app.models.suscriptor.suscriptor import Suscriptor

class Command(BaseCommand):
    help = 'Revisa y corrige los estados de los bloques según el Excel original'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True, help='Ruta al archivo Excel de participantes')
        parser.add_argument('--sheet', type=str, default='0', help='Nombre o índice de la hoja (por defecto: 0)')
        parser.add_argument('--apply', action='store_true', help='Aplicar cambios (por defecto solo reporta)')

    def handle(self, *args, **options):
        file_path = options['file']
        apply_changes = options['apply']
        
        # Intentar convertir sheet_name a entero (índice de hoja)
        try:
            sheet_name = int(options['sheet'])
        except ValueError:
            # Si no es un número, asumimos que es el nombre de la hoja
            sheet_name = options['sheet']
        
        self.stdout.write(self.style.SUCCESS(f"Analizando bloques desde {file_path} (hoja: {sheet_name})"))
        
        # Leer Excel sin encabezados
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        # Índices de columnas relevantes
        COL_BLOQUE = 2       # Número de bloque
        COL_EMAIL = 3        # Email del suscriptor
        COL_VALIDACION = 12  # "VALIDA FOTO"
        COL_ENTREGADO = 13   # "anoto nodo"
        COL_RECIBIDO = 14    # "RECIBIMOS"
        COL_DIPLOMA = 15     # "Diploma OK"
        
        # Estadísticas para reportar
        stats = {
            'total_excel': 0,
            'libre': 0,
            'asignado': 0,
            'validacion': 0,
            'entregado_nodo': 0,
            'recibido_m3d': 0,
            'diploma_entregado': 0,
            'cambios_aplicados': 0,
            'no_encontrados': 0
        }
        
        # Lista para guardar los cambios a aplicar
        cambios = []
        
        # Procesar cada fila del Excel
        for idx, row in df.iterrows():
            # Saltear primera fila si contiene encabezados
            if idx == 0 and isinstance(row[COL_BLOQUE], str) and not row[COL_BLOQUE].strip().startswith(('0', '1', '2', '3', '4', '5', '6')):
                continue
                
            # Obtener número de bloque
            if COL_BLOQUE >= len(row) or pd.isna(row[COL_BLOQUE]):
                continue
                
            numero_bloque = str(row[COL_BLOQUE]).strip()
            if not numero_bloque or numero_bloque.lower() == 'nan':
                continue
                
            stats['total_excel'] += 1
            
            # Determinar el estado correcto según el Excel
            estado = 'libre'
            
            # Obtener email del suscriptor
            email_suscriptor = None
            if COL_EMAIL < len(row) and not pd.isna(row[COL_EMAIL]):
                email_suscriptor = str(row[COL_EMAIL]).strip()
                if email_suscriptor and email_suscriptor.lower() != 'nan':
                    # Si hay email, al menos está asignado
                    estado = 'asignado'
                    stats['asignado'] += 1
            else:
                stats['libre'] += 1
            
            # Verificar estados más avanzados (de mayor a menor prioridad)
            if COL_DIPLOMA < len(row) and not pd.isna(row[COL_DIPLOMA]) and row[COL_DIPLOMA] == 1:
                estado = 'diploma_entregado'
                stats['diploma_entregado'] += 1
            elif COL_RECIBIDO < len(row) and not pd.isna(row[COL_RECIBIDO]) and row[COL_RECIBIDO] == 1:
                estado = 'recibido_m3d'
                stats['recibido_m3d'] += 1
            elif COL_ENTREGADO < len(row) and not pd.isna(row[COL_ENTREGADO]) and row[COL_ENTREGADO] == 1:
                estado = 'entregado_nodo'
                stats['entregado_nodo'] += 1
            elif COL_VALIDACION < len(row) and not pd.isna(row[COL_VALIDACION]) and row[COL_VALIDACION] == 1:
                estado = 'validacion'
                stats['validacion'] += 1
            
            # Comparar con el estado actual en la base de datos
            try:
                bloque = Bloque.objects.get(numero_bloque=numero_bloque)
                if bloque.estado != estado:
                    cambios.append({
                        'bloque': bloque,
                        'estado_actual': bloque.estado,
                        'estado_correcto': estado
                    })
            except Bloque.DoesNotExist:
                stats['no_encontrados'] += 1
                self.stdout.write(self.style.WARNING(f"Bloque {numero_bloque} no encontrado en la base de datos"))
        
        # Reportar estadísticas del Excel
        self.stdout.write("\nEstadísticas de bloques en el Excel:")
        self.stdout.write(f"Total de bloques en Excel: {stats['total_excel']}")
        self.stdout.write(f"- Libres: {stats['libre']}")
        self.stdout.write(f"- Asignados: {stats['asignado']}")
        self.stdout.write(f"- Con foto de validación: {stats['validacion']}")
        self.stdout.write(f"- Entregados en nodo: {stats['entregado_nodo']}")
        self.stdout.write(f"- Recibidos en M3D: {stats['recibido_m3d']}")
        self.stdout.write(f"- Con diploma entregado: {stats['diploma_entregado']}")
        self.stdout.write(f"- No encontrados en BD: {stats['no_encontrados']}")
        
        # Reportar cambios necesarios
        self.stdout.write(f"\nCambios necesarios: {len(cambios)}")
        
        if cambios:
            for i, cambio in enumerate(cambios[:20]):  # Mostrar los primeros 20 cambios
                bloque = cambio['bloque']
                self.stdout.write(f"{i+1}. Bloque {bloque.numero_bloque}: {cambio['estado_actual']} -> {cambio['estado_correcto']}")
            
            if len(cambios) > 20:
                self.stdout.write(f"... y {len(cambios) - 20} más")
            
            # Aplicar cambios si se solicita
            if apply_changes:
                from django.utils import timezone
                now = timezone.now()
                
                for cambio in cambios:
                    bloque = cambio['bloque']
                    nuevo_estado = cambio['estado_correcto']
                    
                    # Actualizar estado y fechas correspondientes
                    bloque.estado = nuevo_estado
                    
                    if nuevo_estado != 'libre':
                        bloque.fecha_asignacion = bloque.fecha_asignacion or now
                    if nuevo_estado in ['validacion', 'entregado_nodo', 'recibido_m3d', 'diploma_entregado']:
                        bloque.fecha_validacion = bloque.fecha_validacion or now
                    if nuevo_estado in ['entregado_nodo', 'recibido_m3d', 'diploma_entregado']:
                        bloque.fecha_entrega_nodo = bloque.fecha_entrega_nodo or now
                    if nuevo_estado in ['recibido_m3d', 'diploma_entregado']:
                        bloque.fecha_recepcion_m3d = bloque.fecha_recepcion_m3d or now
                    if nuevo_estado == 'diploma_entregado':
                        bloque.fecha_entrega_diploma = bloque.fecha_entrega_diploma or now
                    
                    bloque.save()
                    stats['cambios_aplicados'] += 1
                
                self.stdout.write(self.style.SUCCESS(f"\nCambios aplicados: {stats['cambios_aplicados']}"))
            else:
                self.stdout.write(self.style.WARNING("\nNo se aplicaron cambios. Use --apply para aplicar cambios."))
        else:
            self.stdout.write(self.style.SUCCESS("\nNo se requieren cambios. Los estados están correctos."))