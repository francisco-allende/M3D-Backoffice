# m3d_app/management/commands/analizar_valores_excel.py

from django.core.management.base import BaseCommand
import pandas as pd
import collections

class Command(BaseCommand):
    help = 'Analiza los valores presentes en las columnas de estado del Excel'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True, help='Ruta al archivo Excel')
        parser.add_argument('--sheet', type=str, default='0', help='Nombre o índice de la hoja')

    def handle(self, *args, **options):
        file_path = options['file']
        
        # Convertir sheet_name a entero si es posible
        try:
            sheet_name = int(options['sheet'])
        except ValueError:
            sheet_name = options['sheet']
        
        # Leer Excel sin encabezados
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        # Índices de columnas relevantes
        COL_VALIDACION = 12  # "VALIDA FOTO"
        COL_ENTREGADO = 13   # "anoto nodo"
        COL_RECIBIDO = 14    # "RECIBIMOS"
        COL_DIPLOMA = 15     # "Diploma OK"
        
        # Contar los valores distintos en cada columna
        conteos = {
            'VALIDA FOTO': collections.Counter(),
            'anoto nodo': collections.Counter(),
            'RECIBIMOS': collections.Counter(),
            'Diploma OK': collections.Counter()
        }
        
        # Lista de columnas y sus índices
        columnas = [
            ('VALIDA FOTO', COL_VALIDACION),
            ('anoto nodo', COL_ENTREGADO),
            ('RECIBIMOS', COL_RECIBIDO),
            ('Diploma OK', COL_DIPLOMA)
        ]
        
        # Contadores de valores positivos (no nulos, no cero)
        valores_positivos = {nombre: 0 for nombre, _ in columnas}
        
        # Analizar cada columna
        for nombre, idx in columnas:
            if idx < df.shape[1]:
                # Contar valores distintos
                for valor in df[idx].dropna():
                    conteos[nombre][valor] += 1
                    
                    # Contar valores que no son 0, nan, false, etc.
                    if str(valor).strip() not in ['0', 'nan', 'false', 'False', 'no', 'No']:
                        valores_positivos[nombre] += 1
        
        # Mostrar resultados
        self.stdout.write(self.style.SUCCESS(f"Análisis de valores en columnas de estado:"))
        self.stdout.write("=" * 50)
        
        for nombre, contador in conteos.items():
            self.stdout.write(f"\nValores en columna '{nombre}':")
            for valor, count in contador.most_common(10):
                self.stdout.write(f"  - {repr(valor)}: {count} veces")
            
            self.stdout.write(f"\nTotal de valores positivos en '{nombre}': {valores_positivos[nombre]}")
            self.stdout.write("-" * 50)