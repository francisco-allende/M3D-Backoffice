# backoffice/mapa_malvinas/management/commands/asignar_tipos_bloques.py

from django.core.management.base import BaseCommand
import pandas as pd
from mapa_malvinas.models.mapa_bloque.mapa_bloque import MapaBloque
from mapa_malvinas.models.choices.tipo_bloque import TipoBloque

class Command(BaseCommand):
    help = 'Asigna tipos de bloques basado en sus características'

    def add_arguments(self, parser):
        # Argumento para el archivo Excel
        parser.add_argument('--file', type=str, help='Ruta al archivo Excel con datos de bloques')
        # Argumento opcional para la hoja del Excel
        parser.add_argument('--sheet', type=str, default='0', help='Nombre o índice de la hoja (por defecto: 0)')

    def handle(self, *args, **options):
        # Verificar si se proporcionó el archivo
        file_path = options.get('file')
        if not file_path:
            self.stdout.write(self.style.ERROR('Debe especificar un archivo con --file'))
            return

        # Convertir sheet_name a entero si es posible
        try:
            sheet_name = int(options['sheet'])
        except ValueError:
            sheet_name = options['sheet']
        
        # Leer Excel
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al leer el archivo Excel: {str(e)}'))
            return
        
        # Contadores para seguimiento
        conteo_caidos = 0
        conteo_geograficos = 0
        sin_cambios = 0
        
        # Tipos de bloques disponibles
        tipos = dict(TipoBloque.get_all_tipos())
        
        # Procesar cada bloque de MapaBloque
        bloques = MapaBloque.objects.all()
        
        for bloque in bloques:
            # Flag para marcar si se hizo un cambio
            cambio_realizado = False
            
            # Verificar bloques con cruz (Caídos en batalla)
            if '✝' in bloque.descripcion or 'cruz' in bloque.descripcion.lower():
                if bloque.tipo != 'Caídos en batalla':
                    bloque.tipo = 'Caídos en batalla'
                    cambio_realizado = True
                    conteo_caidos += 1
            
            # Verificar bloques en mayúsculas (Geográficos)
            if bloque.descripcion.isupper():
                if bloque.tipo != 'Geográfico':
                    bloque.tipo = 'Geográfico'
                    cambio_realizado = True
                    conteo_geograficos += 1
            
            # Guardar si hubo cambios
            if cambio_realizado:
                bloque.save()
            else:
                sin_cambios += 1
        
        # Mostrar resumen
        self.stdout.write(self.style.SUCCESS('Resultado de la asignación de tipos de bloques:'))
        self.stdout.write(f'- Bloques de Caídos en Batalla: {conteo_caidos}')
        self.stdout.write(f'- Bloques Geográficos: {conteo_geograficos}')
        self.stdout.write(f'- Bloques sin cambios: {sin_cambios}')
        self.stdout.write(f'- Total de bloques procesados: {bloques.count()}')