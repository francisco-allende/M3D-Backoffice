# mapa_malvinas/management/commands/analizar_poster_m3d.py

from django.core.management.base import BaseCommand
import pandas as pd
import re
import os

class Command(BaseCommand):
    help = 'Analiza el Excel de POSTER Secciones y textos MALVINAS3D'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Ruta al archivo Excel (opcional)')
        
    def handle(self, *args, **options):
        # Determinar la ruta del archivo
        file_path = options.get('file')
        if not file_path:
            # Buscar en la raíz del proyecto
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            file_path = os.path.join(base_dir, 'POSTER Secciones y textos MALVINAS3D.xlsx')
            
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"No se encontró el archivo: {file_path}"))
            return
            
        self.stdout.write(f"Analizando archivo: {file_path}")
        
        # Primero intentar leer el Excel para ver su estructura
        try:
            # Cargar todas las hojas para examinarlas
            xls = pd.ExcelFile(file_path)
            sheet_names = xls.sheet_names
            
            self.stdout.write(f"Hojas encontradas: {', '.join(sheet_names)}")
            
            # Contador total de celdas M3D
            total_celdas = 0
            
            # Procesar cada hoja
            for sheet_name in sheet_names:
                self.stdout.write(f"\nProcesando hoja: {sheet_name}")
                
                # Leer la hoja actual
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
                
                # Contar celdas M3D en esta hoja
                celdas_hoja = 0
                
                # Buscar celdas que comienzan con "M3D" en toda la hoja
                for r in range(df.shape[0]):
                    for c in range(df.shape[1]):
                        cell_value = df.iloc[r, c]
                        if pd.notna(cell_value) and isinstance(cell_value, str) and cell_value.strip().startswith("M3D"):
                            text = cell_value.strip()
                            
                            # Extraer sección-número con expresión regular
                            match = re.search(r'M3D\s+(\d{2})\s*-\s*(\d{2})', text)
                            if match:
                                seccion = match.group(1)
                                numero = match.group(2)
                                codigo = f"{seccion}-{numero}"
                                
                                # Obtener el texto después del código
                                # Primero extraer el patrón completo que coincidió
                                full_match = match.group(0)  # Ej: "M3D 05 - 20"
                                # Eliminar el patrón del texto para obtener solo el contenido
                                content = text[text.find(full_match) + len(full_match):].strip()
                                
                                # Imprimir la línea formateada
                                self.stdout.write(f"M3D {codigo} {content}")
                                celdas_hoja += 1
                            else:
                                # Si no coincide con el formato esperado, pero comienza con M3D
                                self.stdout.write(self.style.WARNING(f"Formato no reconocido: {text}"))
                
                total_celdas += celdas_hoja
                self.stdout.write(f"Total celdas M3D en hoja {sheet_name}: {celdas_hoja}")
            
            # Mostrar el total general
            self.stdout.write(self.style.SUCCESS(f"\nTotal de celdas M3D encontradas: {total_celdas}"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al procesar el archivo: {str(e)}"))