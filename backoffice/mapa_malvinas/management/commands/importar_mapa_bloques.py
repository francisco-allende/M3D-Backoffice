# mapa_malvinas/management/commands/importar_mapa_bloques.py

from django.core.management.base import BaseCommand
import pandas as pd
import re
import os
from mapa_malvinas.models.mapa_bloque.mapa_bloque import MapaBloque
from django.db import transaction

class Command(BaseCommand):
    help = 'Importa los 1500 bloques del Excel de POSTER Secciones y textos MALVINAS3D'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Ruta al archivo Excel (opcional)')
        parser.add_argument('--dry-run', action='store_true', help='Simular sin guardar en la base de datos')
        
    def handle(self, *args, **options):
        # Determinar la ruta del archivo
        file_path = options.get('file')
        dry_run = options.get('dry_run', False)
        
        if not file_path:
            # Buscar en la raíz del proyecto
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            file_path = os.path.join(base_dir, 'POSTER Secciones y textos MALVINAS3D.xlsx')
            
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"No se encontró el archivo: {file_path}"))
            return
            
        self.stdout.write(f"Analizando archivo: {file_path}")
        
        try:
            # Cargar todas las hojas
            xls = pd.ExcelFile(file_path)
            sheet_names = xls.sheet_names
            
            # Contadores para seguimiento
            bloques_encontrados = 0
            bloques_creados = 0
            bloques_actualizados = 0
            
            # Lista para almacenar todos los bloques antes de guardarlos
            bloques_a_guardar = []
            
            # Procesar cada hoja
            for sheet_name in sheet_names:
                self.stdout.write(f"\nProcesando hoja: {sheet_name}")
                
                # Leer la hoja actual
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                
                # Buscar celdas que comienzan con "M3D" o "MD3" (para capturar el error tipográfico)
                for r in range(df.shape[0]):
                    for c in range(df.shape[1]):
                        cell_value = df.iloc[r, c]
                        # Verificar si la celda contiene texto
                        if pd.notna(cell_value) and isinstance(cell_value, str):
                            text = cell_value.strip()
                            
                            # Comprobar si es un bloque M3D o el error MD3
                            is_m3d = text.startswith("M3D")
                            is_md3 = text.startswith("MD3")  # Capturar el error tipográfico
                            
                            if is_m3d or is_md3:
                                bloques_encontrados += 1
                                
                                # Extraer el código, sección y número
                                if is_m3d:
                                    # Formato normal: M3D SS-NN
                                    match = re.search(r'M3D\s+(\d{2})\s*-\s*(\d{2})', text)
                                    prefijo = "M3D"
                                else:
                                    # Formato con error: MD3 SS-NN
                                    match = re.search(r'MD3\s+(\d{2})\s*-\s*(\d{2})', text)
                                    prefijo = "MD3"  # Mantener el error como está en el Excel
                                
                                if match:
                                    seccion = match.group(1)
                                    numero = match.group(2)
                                    # Construir código normalizado
                                    codigo = f"{prefijo} {seccion}-{numero}"
                                    # Construir numero_bloque normalizado
                                    numero_bloque = f"{seccion}-{numero}"
                                    
                                    # Si no hay errores, crear o actualizar el bloque en la base de datos
                                    if not dry_run:
                                        try:
                                            bloque, created = MapaBloque.objects.get_or_create(
                                                codigo=codigo,
                                                defaults={
                                                    'seccion': seccion,
                                                    'numero': numero,
                                                    'numero_bloque': numero_bloque,
                                                    'descripcion': text,
                                                }
                                            )
                                            
                                            if created:
                                                bloques_creados += 1
                                            else:
                                                # Actualizar la descripción
                                                bloque.descripcion = text
                                                bloque.save()
                                                bloques_actualizados += 1
                                                
                                        except Exception as e:
                                            self.stdout.write(self.style.ERROR(f"Error guardando bloque {codigo}: {str(e)}"))
                                    else:
                                        # Solo imprimir en modo simulación
                                        self.stdout.write(f"  - {codigo} (Simulación)")
                                        bloques_creados += 1
                                else:
                                    # Si no se pudo extraer el patrón pero comienza con M3D/MD3
                                    self.stdout.write(self.style.WARNING(f"No se pudo extraer sección-número de: {text[:50]}..."))
            
            # Mostrar resumen
            self.stdout.write(self.style.SUCCESS(f"\nTotal de bloques encontrados: {bloques_encontrados}"))
            if dry_run:
                self.stdout.write(self.style.WARNING(f"Modo simulación: {bloques_creados} bloques serían creados/actualizados"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Bloques creados: {bloques_creados}"))
                self.stdout.write(self.style.SUCCESS(f"Bloques actualizados: {bloques_actualizados}"))
            
            # Verificar si encontramos los 1500 bloques esperados
            if bloques_encontrados != 1500:
                self.stdout.write(self.style.WARNING(f"¡Atención! Se encontraron {bloques_encontrados} bloques cuando se esperaban 1500"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al procesar el archivo: {str(e)}"))