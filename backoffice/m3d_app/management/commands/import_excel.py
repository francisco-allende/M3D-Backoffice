from django.core.management.base import BaseCommand, CommandError
import logging
import os
from m3d_app.utils.excel_manager import ExcelManager
#te amo mucho
class Command(BaseCommand):
    help = 'Importa datos de suscriptores desde archivos Excel'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Ruta al archivo Excel')
        parser.add_argument('--type', type=str, choices=[
            'particulares_con_impresora',
            'particulares_sin_impresora',
            'instituciones_con_impresora',
            'instituciones_sin_impresora',
            'nodos_recepcion',
            'bloques_participantes'
        ], help='Tipo de datos a importar')
        parser.add_argument('--sheet', type=str, default='0', help='Nombre o índice de la hoja (por defecto: 0)')

    def handle(self, *args, **options):
        # Configurar logging
        logger = logging.getLogger('excel_import')
        handler = logging.StreamHandler(self.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        file_path = options['file']
        import_type = options['type']
        sheet_name = options['sheet']
        
        if not file_path:
            raise CommandError('Debe especificar un archivo Excel con --file')
        
        if not import_type:
            raise CommandError('Debe especificar el tipo de datos a importar con --type')
        
        if not os.path.exists(file_path):
            raise CommandError(f'El archivo {file_path} no existe')
        
        try:
            # Intentar convertir sheet_name a entero (índice de hoja)
            sheet_name = int(sheet_name)
        except ValueError:
            # Si no es un número, asumimos que es el nombre de la hoja
            pass
        
        self.stdout.write(self.style.SUCCESS(f'Importando datos de tipo "{import_type}" desde {file_path} (hoja: {sheet_name})'))
        
        # Inicializar el gestor de Excel con el logger
        excel_manager = ExcelManager(logger=logger)
        
        try:
            # Ejecutar la importación según el tipo de datos
            method_name = f'import_{import_type}'
            if not hasattr(excel_manager, method_name):
                raise CommandError(f'Tipo de importación no válido: {import_type}')
            
            import_method = getattr(excel_manager, method_name)
            
            # Manejar de forma diferente según el tipo de importación
            if import_type == 'bloques_participantes':
                registros_creados, registros_actualizados, registros_con_error = import_method(file_path, sheet_name)
                self.stdout.write(self.style.SUCCESS(
                    f'Importación completada: {registros_creados} registros creados, {registros_actualizados} registros actualizados, {registros_con_error} registros con error'
                ))
            else:
                registros_creados, registros_con_error = import_method(file_path, sheet_name)
                self.stdout.write(self.style.SUCCESS(
                    f'Importación completada: {registros_creados} registros creados, {registros_con_error} registros con error'
                ))
            
        except Exception as e:
            import traceback
            self.stdout.write(self.style.ERROR(f'Error detallado: {traceback.format_exc()}'))
            raise CommandError(f'Error durante la importación: {str(e)}')