from django.db import transaction
import pandas as pd
from django.utils import timezone
from .base import ExcelManagerBase
from m3d_app.models.suscriptor.suscriptor import Suscriptor
from m3d_app.models.nodos.nodo_recepcion import NodoRecepcion
from m3d_app.models.bloque3d.bloque import Bloque

class ExcelManagerForBloques(ExcelManagerBase):
    """
    Gestor de Excel especializado en la importación de bloques.
    """
    
    @transaction.atomic
    def import_bloques_participantes(self, file_path, sheet_name=0):
        """
        Importa datos de bloques y su asignación a suscriptores desde Excel.
        Respeta la jerarquía de estados y maneja correctamente bloques múltiples.
        
        Args:
            file_path: Ruta al archivo Excel.
            sheet_name: Nombre o índice de la hoja a leer.
            
        Returns:
            Tuple: (bloques_creados, bloques_actualizados, bloques_con_error)
        """
        # Leer Excel
        df = self.read_excel(file_path, sheet_name)
        
        self.log(f"Archivo leído correctamente. Dimensiones: {df.shape}", 'info')
        
        # Contadores para seguimiento
        bloques_creados = 0
        bloques_actualizados = 0
        bloques_con_error = 0
        estados_count = {'libre': 0, 'asignado': 0, 'validacion': 0, 'entregado_nodo': 0, 'recibido_m3d': 0, 'diploma_entregado': 0}
        
        # Identificar columnas relevantes
        col_bloque = self.find_column(df, ['bloque'])
        col_email = self.find_column(df, ['mail', 'email', 'correo'])
        col_validacion = self.find_column(df, ['valida foto', 'validacion', 'foto'])
        col_entregado = self.find_column(df, ['anoto nodo', 'entregado', 'nodo'])
        col_recibido = self.find_column(df, ['recibimos', 'recibido'])
        col_diploma = self.find_column(df, ['diploma', 'ok'])
        
        if not col_bloque or not col_email:
            self.log(f"No se encontraron columnas básicas: bloque={col_bloque}, email={col_email}", 'error')
            return 0, 0, 0
        
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
            self.log("No se encontró ninguna columna de estado", 'error')
            return 0, 0, 0
            
        self.log(f"Columnas identificadas: bloque={col_bloque}, email={col_email}", 'info')
        self.log(f"Estados encontrados: {', '.join(estados_encontrados)}", 'info')
        
        # Definir la jerarquía de estados
        jerarquia_estados = {
            'libre': 0,
            'asignado': 1,
            'validacion': 2,
            'entregado_nodo': 3,
            'recibido_m3d': 4,
            'diploma_entregado': 5
        }
        
        # Preparar estructuras de datos
        bloques_info = {}  # Almacenará {numero_bloque: {email, estado_maximal}}
        ultima_institucion_email = None
        bloques_institucion = []
        
        # Procesar cada fila del Excel
        for idx, row in df.iterrows():
            try:
                # Obtener información básica
                if pd.isna(row[col_bloque]):
                    continue
                    
                numero_bloque = str(row[col_bloque]).strip()
                
                # Obtener email del suscriptor
                email_suscriptor = None
                if col_email in row and not pd.isna(row[col_email]):
                    email_suscriptor = str(row[col_email]).strip()
                
                # Si es una fila vacía de una institución (que tiene 3 bloques)
                if not email_suscriptor or email_suscriptor == "":
                    # Si ya procesamos una institución, podría ser uno de sus bloques adicionales
                    if ultima_institucion_email and len(bloques_institucion) < 3:
                        self.log(f"Fila {idx+1}: Asignando bloque adicional a la institución con email {ultima_institucion_email}", 'info')
                        email_suscriptor = ultima_institucion_email
                        bloques_institucion.append(numero_bloque)
                    else:
                        # Si no hay email y no pertenece a una institución ya procesada, es un bloque libre
                        self.log(f"Fila {idx+1}: No hay email, bloque libre", 'info')
                        bloques_info[numero_bloque] = {
                            'email': None,
                            'estado': 'libre'
                        }
                        estados_count['libre'] += 1
                        continue
                
                # Verificar si es una institución (para seguimiento de bloques múltiples)
                try:
                    suscriptor = Suscriptor.objects.get(email=email_suscriptor)
                    if suscriptor.tipo == 'institucion':
                        ultima_institucion_email = email_suscriptor
                        bloques_institucion = [numero_bloque]
                        self.log(f"Fila {idx+1}: Institución encontrada: {email_suscriptor}", 'info')
                    else:
                        # Si es particular, reiniciar seguimiento de instituciones
                        ultima_institucion_email = None
                        bloques_institucion = []
                except Suscriptor.DoesNotExist:
                    # Si no existe, asumimos que no es institución
                    ultima_institucion_email = None
                    bloques_institucion = []
                    self.log(f"Fila {idx+1}: Suscriptor no encontrado: {email_suscriptor}", 'warning')
                
                # Iniciar con estado mínimo si hay email
                estado_maximal = 'asignado'
                
                # Verificar cada estado posible en orden inverso (del más alto al más bajo)
                if col_diploma and not pd.isna(row[col_diploma]) and row[col_diploma] == 1:
                    estado_maximal = 'diploma_entregado'
                    self.log(f"Fila {idx+1}: Estado diploma_entregado para bloque {numero_bloque}", 'info')
                elif col_recibido and not pd.isna(row[col_recibido]) and row[col_recibido] == 1:
                    estado_maximal = 'recibido_m3d'
                    self.log(f"Fila {idx+1}: Estado recibido_m3d para bloque {numero_bloque}", 'info')
                elif col_entregado and not pd.isna(row[col_entregado]) and row[col_entregado] == 1:
                    estado_maximal = 'entregado_nodo'
                    self.log(f"Fila {idx+1}: Estado entregado_nodo para bloque {numero_bloque}", 'info')
                elif col_validacion and not pd.isna(row[col_validacion]) and row[col_validacion] == 1:
                    estado_maximal = 'validacion'
                    self.log(f"Fila {idx+1}: Estado validacion para bloque {numero_bloque}", 'info')
                
                # Guardar la información
                bloques_info[numero_bloque] = {
                    'email': email_suscriptor,
                    'estado': estado_maximal
                }
                
                # Actualizar contadores
                estados_count[estado_maximal] += 1
                
            except Exception as e:
                bloques_con_error += 1
                self.log(f"Error procesando fila {idx+1}: {str(e)}", 'error')
        
        # Mostrar resumen del análisis
        self.log("\nResumen de bloques por estado:", 'info')
        for estado, count in estados_count.items():
            self.log(f"  - {estado}: {count}", 'info')
        
        # Fecha actual para campos de fecha
        now = timezone.now()
        
        # Actualizar la base de datos
        for numero_bloque, info in bloques_info.items():
            try:
                # Si no hay email asociado, es un bloque libre
                if not info['email']:
                    try:
                        bloque, created = Bloque.objects.update_or_create(
                            numero_bloque=numero_bloque,
                            defaults={
                                'suscriptor': None,
                                'estado': 'libre',
                                'fecha_asignacion': None,
                                'fecha_validacion': None,
                                'fecha_entrega_nodo': None,
                                'fecha_recepcion_m3d': None,
                                'fecha_entrega_diploma': None
                            }
                        )
                        
                        if created:
                            bloques_creados += 1
                            self.log(f"Bloque {numero_bloque} creado con estado libre", 'info')
                        else:
                            bloques_actualizados += 1
                            self.log(f"Bloque {numero_bloque} actualizado a estado libre", 'info')
                            
                    except Exception as e:
                        bloques_con_error += 1
                        self.log(f"Error creando/actualizando bloque libre {numero_bloque}: {str(e)}", 'error')
                    
                    continue
                
                # Buscar el suscriptor por email
                try:
                    suscriptor = Suscriptor.objects.get(email=info['email'])
                    
                    # Buscar el nodo asociado al suscriptor (si existe)
                    nodo_recepcion = NodoRecepcion.objects.filter(suscriptor=suscriptor).first()
                    
                    # Preparar datos del bloque
                    bloque_data = {
                        'suscriptor': suscriptor,
                        'nodo_recepcion': nodo_recepcion,
                        'estado': info['estado']
                    }
                    
                    # Establecer fechas según el estado
                    if info['estado'] != 'libre':
                        bloque_data['fecha_asignacion'] = now
                    if info['estado'] in ['validacion', 'entregado_nodo', 'recibido_m3d', 'diploma_entregado']:
                        bloque_data['fecha_validacion'] = now
                    if info['estado'] in ['entregado_nodo', 'recibido_m3d', 'diploma_entregado']:
                        bloque_data['fecha_entrega_nodo'] = now
                    if info['estado'] in ['recibido_m3d', 'diploma_entregado']:
                        bloque_data['fecha_recepcion_m3d'] = now
                    if info['estado'] == 'diploma_entregado':
                        bloque_data['fecha_entrega_diploma'] = now
                    
                    # Extraer sección y número del numero_bloque al guardar
                    try:
                        if '-' in numero_bloque:
                            partes = numero_bloque.split('-')
                            if len(partes) == 2:
                                bloque_data['seccion'] = partes[0].strip()
                                bloque_data['numero'] = partes[1].strip()
                    except Exception as e:
                        self.log(f"Error extrayendo sección y número para bloque {numero_bloque}: {str(e)}", 'warning')
                    
                    # Crear o actualizar el bloque
                    bloque, created = Bloque.objects.update_or_create(
                        numero_bloque=numero_bloque,
                        defaults=bloque_data
                    )
                    
                    if created:
                        bloques_creados += 1
                        self.log(f"Bloque {numero_bloque} creado con estado {info['estado']}", 'info')
                    else:
                        bloques_actualizados += 1
                        self.log(f"Bloque {numero_bloque} actualizado a estado {info['estado']}", 'info')
                    
                except Suscriptor.DoesNotExist:
                    bloques_con_error += 1
                    self.log(f"No se encontró suscriptor con email {info['email']} para bloque {numero_bloque}", 'error')
                except Exception as e:
                    bloques_con_error += 1
                    self.log(f"Error creando/actualizando bloque {numero_bloque}: {str(e)}", 'error')
                    
            except Exception as e:
                bloques_con_error += 1
                self.log(f"Error general procesando bloque {numero_bloque}: {str(e)}", 'error')
        
        # Mostrar resumen final
        self.log(f"\nImportación completada: {bloques_creados} bloques creados, {bloques_actualizados} bloques actualizados, {bloques_con_error} bloques con error", 'info')
        
        # Mostrar estadísticas finales en la base de datos
        estados_finales = {}
        for estado in jerarquia_estados.keys():
            estados_finales[estado] = Bloque.objects.filter(estado=estado).count()
        
        self.log("\nEstado final en la base de datos:", 'info')
        for estado, count in estados_finales.items():
            self.log(f"  - {estado}: {count}", 'info')
        
        return bloques_creados, bloques_actualizados, bloques_con_error