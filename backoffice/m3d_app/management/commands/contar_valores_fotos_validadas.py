# backoffice/m3d_app/management/commands/update_blocks_hierarchy.py

from django.core.management.base import BaseCommand, CommandError
import pandas as pd
import os
from django.db import transaction
from m3d_app.models.bloque3d.bloque import Bloque
from m3d_app.models.suscriptor.suscriptor import Suscriptor
from django.utils import timezone

class Command(BaseCommand):
    help = 'Actualiza los bloques respetando jerarquía de estados'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Ruta al archivo Excel')
        parser.add_argument('--sheet', type=str, default='0', help='Nombre o índice de la hoja (por defecto: 0)')
        parser.add_argument('--dry-run', action='store_true', help='Solo mostrar cambios sin aplicarlos')

    def handle(self, *args, **options):
        file_path = options['file']
        sheet_name = options['sheet']
        dry_run = options['dry_run']
        
        if not file_path:
            raise CommandError('Debe especificar un archivo Excel con --file')
        
        if not os.path.exists(file_path):
            raise CommandError(f'El archivo {file_path} no existe')
        
        try:
            # Intentar convertir sheet_name a entero (índice de hoja)
            sheet_name = int(sheet_name)
        except ValueError:
            # Si no es un número, asumimos que es el nombre de la hoja
            pass
        
        self.stdout.write(f'Analizando archivo Excel: {file_path} (hoja: {sheet_name})')
        
        # Leer Excel
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Mostrar información básica
        self.stdout.write(f'Dimensiones del DataFrame: {df.shape}')
        
        # Identificar columnas relevantes
        def find_column(search_terms):
            for col in df.columns:
                col_str = str(col).lower()
                if any(term.lower() in col_str for term in search_terms):
                    return col
            return None
        
        col_bloque = find_column(['bloque'])
        col_email = find_column(['mail', 'email', 'correo'])
        col_validacion = find_column(['valida foto', 'validacion', 'foto'])
        col_entregado = find_column(['anoto nodo', 'entregado', 'nodo'])
        col_recibido = find_column(['recibimos', 'recibido'])
        col_diploma = find_column(['diploma', 'ok', 'diploma ok'])
        
        if not col_bloque or not col_email:
            self.stdout.write(self.style.ERROR(f'No se encontraron columnas básicas: bloque={col_bloque}, email={col_email}'))
            return
        
        # Verificar columnas de estado
        estados_encontrados = []
        if col_validacion:
            estados_encontrados.append('validacion')
        if col_entregado:
            estados_encontrados.append('entregado_nodo')
        if col_recibido:
            estados_encontrados.append('recibido_m3d')
        if col_diploma:
            estados_encontrados.append('diploma_entregado')
            
        if not estados_encontrados:
            self.stdout.write(self.style.ERROR('No se encontró ninguna columna de estado'))
            return
            
        self.stdout.write(f'Columnas identificadas: bloque={col_bloque}, email={col_email}')
        self.stdout.write(f'Estados encontrados: {", ".join(estados_encontrados)}')
        
        # Definir la jerarquía de estados
        # Orden: libre -> asignado -> validacion -> entregado_nodo -> recibido_m3d -> diploma_entregado
        jerarquia_estados = {
            'libre': 0,
            'asignado': 1,
            'validacion': 2,
            'entregado_nodo': 3,
            'recibido_m3d': 4,
            'diploma_entregado': 5
        }
        
        # Contadores para análisis
        conteos = {estado: 0 for estado in jerarquia_estados.keys()}
        conteos_netos = {estado: 0 for estado in jerarquia_estados.keys()}
        
        # Preparar estructuras de datos
        bloques_info = {}  # Almacenará {numero_bloque: {email, estado_maximal}}
        
        # Procesar cada fila del Excel
        for _, row in df.iterrows():
            try:
                # Obtener información básica
                if pd.isna(row[col_bloque]) or pd.isna(row[col_email]):
                    continue
                    
                numero_bloque = str(row[col_bloque]).strip()
                email = str(row[col_email]).strip()
                
                # Iniciar con estado mínimo si hay email
                estado_maximal = 'asignado'
                
                # Verificar cada estado posible
                if col_diploma and not pd.isna(row[col_diploma]) and row[col_diploma] == 1:
                    estado_maximal = 'diploma_entregado'
                elif col_recibido and not pd.isna(row[col_recibido]) and row[col_recibido] == 1:
                    estado_maximal = 'recibido_m3d'
                elif col_entregado and not pd.isna(row[col_entregado]) and row[col_entregado] == 1:
                    estado_maximal = 'entregado_nodo'
                elif col_validacion and not pd.isna(row[col_validacion]) and row[col_validacion] == 1:
                    estado_maximal = 'validacion'
                
                # Guardar la información
                bloques_info[numero_bloque] = {
                    'email': email,
                    'estado': estado_maximal
                }
                
                # Actualizar contadores
                conteos[estado_maximal] += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error procesando fila: {str(e)}'))
        
        # Calcular conteos netos (bloques que están en ese estado exacto)
        for estado, nivel in jerarquia_estados.items():
            # Para cada estado, contar bloques que están en ese nivel exacto
            conteos_netos[estado] = sum(1 for info in bloques_info.values() if info['estado'] == estado)
        
        # Mostrar resultados del análisis
        self.stdout.write("\nConteo total de bloques por estado maximal:")
        for estado in jerarquia_estados.keys():
            self.stdout.write(f"  - {estado}: {conteos[estado]}")
            
        self.stdout.write("\nConteo neto de bloques por estado exacto:")
        for estado in jerarquia_estados.keys():
            self.stdout.write(f"  - {estado}: {conteos_netos[estado]}")
        
        # Actualizar la base de datos
        if dry_run:
            self.stdout.write(self.style.WARNING('\nModo simulación: no se aplicarán cambios'))
            return
            
        with transaction.atomic():
            # Restablecer todos los bloques a estado básico
            Bloque.objects.all().update(
                estado='libre',
                fecha_asignacion=None,
                fecha_validacion=None,
                fecha_entrega_nodo=None,
                fecha_recepcion_m3d=None,
                fecha_entrega_diploma=None
            )
            self.stdout.write('Se restablecieron todos los bloques a estado "libre"')
            
            # Fecha actual para campos de fecha
            now = timezone.now()
            
            # Actualizar cada bloque según su estado maximal
            actualizados = 0
            errores = 0
            
            for numero_bloque, info in bloques_info.items():
                try:
                    # Buscar el bloque y el suscriptor
                    try:
                        bloque = Bloque.objects.get(numero_bloque=numero_bloque)
                        suscriptor = Suscriptor.objects.get(email=info['email'])
                        
                        # Preparar datos según el estado
                        bloque_data = {
                            'suscriptor': suscriptor,
                            'estado': info['estado']
                        }
                        
                        # Establecer fechas según el estado
                        if info['estado'] != 'libre':
                            bloque.fecha_asignacion = now
                        if info['estado'] in ['validacion', 'entregado_nodo', 'recibido_m3d', 'diploma_entregado']:
                            bloque.fecha_validacion = now
                        if info['estado'] in ['entregado_nodo', 'recibido_m3d', 'diploma_entregado']:
                            bloque.fecha_entrega_nodo = now
                        if info['estado'] in ['recibido_m3d', 'diploma_entregado']:
                            bloque.fecha_recepcion_m3d = now
                        if info['estado'] == 'diploma_entregado':
                            bloque.fecha_entrega_diploma = now
                        
                        # Actualizar el estado del bloque
                        bloque.suscriptor = suscriptor
                        bloque.estado = info['estado']
                        bloque.save()
                        
                        actualizados += 1
                        
                    except Bloque.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f'No se encontró el bloque {numero_bloque}'))
                        errores += 1
                    except Suscriptor.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f'No se encontró el suscriptor con email {info["email"]}'))
                        errores += 1
                        
                except Exception as e:
                    errores += 1
                    self.stdout.write(self.style.ERROR(f'Error actualizando bloque {numero_bloque}: {str(e)}'))
            
            # Mostrar resultado final
            self.stdout.write(self.style.SUCCESS(f'\nSe actualizaron {actualizados} bloques'))
            if errores > 0:
                self.stdout.write(self.style.ERROR(f'Se encontraron {errores} errores durante el proceso'))
            
            # Verificar resultado final en la base de datos
            estados_db = {}
            for estado in jerarquia_estados.keys():
                estados_db[estado] = Bloque.objects.filter(estado=estado).count()
                
            self.stdout.write("\nEstado final en la base de datos:")
            for estado, count in estados_db.items():
                self.stdout.write(f"  - {estado}: {count}")
                
            # Comparar con los conteos esperados
            self.stdout.write("\nComparación con valores esperados:")
            total_correcto = True
            for estado in jerarquia_estados.keys():
                if estados_db[estado] == conteos_netos[estado]:
                    self.stdout.write(self.style.SUCCESS(f"  ✓ {estado}: {estados_db[estado]} (coincide)"))
                else:
                    total_correcto = False
                    self.stdout.write(self.style.ERROR(f"  ✗ {estado}: {estados_db[estado]} (esperado: {conteos_netos[estado]})"))
            
            if total_correcto:
                self.stdout.write(self.style.SUCCESS("\n¡Todos los estados coinciden con los valores esperados!"))
            else:
                self.stdout.write(self.style.ERROR("\nAlgunos estados no coinciden con los valores esperados"))