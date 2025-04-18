from django.core.management.base import BaseCommand
import pandas as pd
from m3d_app.models.suscriptor.suscriptor import Suscriptor
from m3d_app.models.suscriptor.particular_sin_impresora import ParticularSinImpresora
from django.db import transaction
import os

class Command(BaseCommand):
    help = 'Importa suscriptores faltantes desde el Excel de participantes'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, required=True, help='Ruta al archivo Excel de participantes')
        parser.add_argument('--sheet', type=str, default='0', help='Nombre o índice de la hoja (por defecto: 0)')

    def handle(self, *args, **options):
        file_path = options['file']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"El archivo {file_path} no existe"))
            return
            
        # Intentar convertir sheet_name a entero (índice de hoja)
        try:
            sheet_name = int(options['sheet'])
        except ValueError:
            # Si no es un número, asumimos que es el nombre de la hoja
            sheet_name = options['sheet']
        
        self.stdout.write(self.style.SUCCESS(f"Importando suscriptores desde {file_path} (hoja: {sheet_name})"))
        
        # Leer Excel
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Índice de columnas relevantes (ajustar según la estructura real del Excel)
        COL_EMAIL = 3  # Columna con email del suscriptor
        
        # Verificar que la columna de email existe
        if COL_EMAIL >= df.shape[1]:
            self.stdout.write(self.style.ERROR(f"La columna de email (índice {COL_EMAIL}) no existe en el archivo"))
            return
            
        # Contadores
        suscriptores_creados = 0
        suscriptores_ya_existentes = 0
        errores = 0
        
        # Procesar cada fila del Excel
        for idx, row in df.iterrows():
            try:
                # Obtener email del suscriptor
                if pd.isna(row[COL_EMAIL]):
                    continue
                    
                email = str(row[COL_EMAIL]).strip()
                if not email or email.lower() == 'nan':
                    continue
                
                # Verificar si el suscriptor ya existe
                if Suscriptor.objects.filter(email=email).exists():
                    suscriptores_ya_existentes += 1
                    continue
                
                # Obtener otros datos del suscriptor
                nombre = ""
                if 'NOMBRE' in df.columns and not pd.isna(row['NOMBRE']):
                    nombre = str(row['NOMBRE']).strip()
                
                apellido = ""  # Asumir que el apellido está incluido en el campo NOMBRE
                
                telefono = ""
                if 'Telefono' in df.columns and not pd.isna(row['Telefono']):
                    telefono = str(row['Telefono']).strip()
                
                provincia = ""
                if 'Provincia' in df.columns and not pd.isna(row['Provincia']):
                    provincia = str(row['Provincia']).strip()
                
                direccion = ""
                if 'Direccion' in df.columns and not pd.isna(row['Direccion']):
                    direccion = str(row['Direccion']).strip()
                
                codigo_postal = ""
                if 'Codigo Postal' in df.columns and not pd.isna(row['Codigo Postal']):
                    codigo_postal = str(row['Codigo Postal']).strip()
                
                # Crear el suscriptor con datos mínimos
                with transaction.atomic():
                    suscriptor = Suscriptor.objects.create(
                        email=email,
                        nombre=nombre[:100],  # Limitar a 100 caracteres
                        apellido=apellido[:100] if apellido else None,
                        telefono=telefono[:20] or "0000000000",
                        calle=direccion[:200] or "Sin datos",
                        numero="S/N",
                        codigo_postal=codigo_postal[:10] or "0000",
                        ciudad="Sin datos",
                        provincia=provincia[:100] or "Sin datos",
                        tipo='particular'
                    )
                    
                    # Crear ParticularSinImpresora asociado
                    ParticularSinImpresora.objects.create(suscriptor=suscriptor)
                    
                    suscriptores_creados += 1
                    self.stdout.write(f"Suscriptor creado: {suscriptor.email} - {suscriptor.nombre}")
                
            except Exception as e:
                errores += 1
                self.stdout.write(self.style.ERROR(f"Error en fila {idx+1}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"Importación completada: {suscriptores_creados} suscriptores creados, "
            f"{suscriptores_ya_existentes} ya existían, {errores} errores"
        ))