import pandas as pd
import re
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from m3d_app.models.suscriptor.suscriptor import Suscriptor
from m3d_app.models.impresora.impresora import Impresora
from m3d_app.models.suscriptor.particular_con_impresora import ParticularConImpresora
from m3d_app.models.suscriptor.particular_sin_impresora import ParticularSinImpresora
from m3d_app.models.suscriptor.institucion_con_impresora import InstitucionConImpresora
from m3d_app.models.suscriptor.institucion_sin_impresora import InstitucionSinImpresora
from m3d_app.models.nodos.nodo_recepcion import NodoRecepcion
from m3d_app.models.bloque3d.bloque import Bloque
from m3d_app.utils.excel_mapper import ExcelMapper
from m3d_app.utils.excel_parser import ExcelParser


class ExcelManager:
    """
    Clase para importar datos desde archivos Excel a la base de datos Django.
    """
    
    def __init__(self, logger=None):
        """
        Inicializa el gestor de Excel.
        
        Args:
            logger: Objeto de registro para guardar mensajes de depuración y errores.
        """
        self.logger = logger
        
    def log(self, message, level='info'):
        """
        Registra un mensaje utilizando el logger proporcionado.
        
        Args:
            message: Mensaje a registrar.
            level: Nivel de registro ('info', 'warning', 'error', etc.).
        """
        if self.logger:
            log_method = getattr(self.logger, level, self.logger.info)
            log_method(message)
        else:
            print(f"[{level.upper()}] {message}")
            
    def read_excel(self, file_path, sheet_name=0):
        """
        Lee un archivo Excel y devuelve un DataFrame de pandas.
        
        Args:
            file_path: Ruta al archivo Excel.
            sheet_name: Nombre o índice de la hoja a leer (por defecto: 0 - primera hoja).
            
        Returns:
            DataFrame de pandas con los datos del Excel.
        """
        try:
            return pd.read_excel(file_path, sheet_name=sheet_name)
        except Exception as e:
            self.log(f"Error al leer el archivo Excel {file_path}: {str(e)}", 'error')
            raise
 
    @transaction.atomic
    def import_particulares_con_impresora(self, file_path, sheet_name=0):
        """
        Importa datos de particulares con impresora desde un Excel.
        
        Args:
            file_path: Ruta al archivo Excel.
            sheet_name: Nombre o índice de la hoja a leer.
            
        Returns:
            Tuple: (registros_creados, registros_con_error)
        """
        df = self.read_excel(file_path, sheet_name)
        
        # Contadores para seguimiento
        registros_creados = 0
        registros_con_error = 0
        
        # Obtener los mapeos de columnas del ExcelMapper
        columnas_suscriptor = ExcelMapper.columnas_suscriptor_part_con_imp()
        columnas_impresora = ExcelMapper.columnas_impresora_part_con_imp()
        
        # Procesar cada fila del Excel
        for idx, row in df.iterrows():
            try:
                with transaction.atomic():
                    # Crear suscriptor
                    suscriptor_data = {}
                    for col_excel, campo_modelo in columnas_suscriptor.items():
                        if col_excel in row and pd.notna(row[col_excel]):
                            # Procesar campos especiales
                            if campo_modelo == 'telefono':
                                suscriptor_data[campo_modelo] = ExcelParser.clean_phone_number(row[col_excel])
                            elif campo_modelo == 'fecha_nacimiento':
                                suscriptor_data[campo_modelo] = ExcelParser.parse_date(row[col_excel])
                            else:
                                suscriptor_data[campo_modelo] = row[col_excel]
                    
                    # Añadir tipo suscriptor
                    suscriptor_data['tipo'] = 'particular'
                    
                    # Crear o actualizar suscriptor por email
                    email = suscriptor_data.get('email')
                    if not email:
                        self.log(f"Fila {idx+2} sin email, omitiendo", 'warning')
                        registros_con_error += 1
                        continue
                    
                    suscriptor, created = Suscriptor.objects.update_or_create(
                        email=email,
                        defaults=suscriptor_data
                    )
                    
                    # Crear impresora
                    impresora_data = {}
                    for col_excel, campo_modelo in columnas_impresora.items():
                        if col_excel in row and pd.notna(row[col_excel]):
                            # Procesar campos especiales
                            if campo_modelo == 'anios_experiencia':
                                impresora_data[campo_modelo] = ExcelParser.parse_years_experience(row[col_excel])
                            elif campo_modelo == 'cantidad_equipos':
                                impresora_data[campo_modelo] = ExcelParser.parse_equipment_count(row[col_excel])
                            else:
                                impresora_data[campo_modelo] = row[col_excel]
                    
                    impresora = Impresora.objects.create(**impresora_data)
                    
                    # Crear relación particular con impresora
                    ParticularConImpresora.objects.update_or_create(
                        suscriptor=suscriptor,
                        defaults={'impresora': impresora}
                    )
                    
                    registros_creados += 1
                    self.log(f"Fila {idx+2}: Particular con impresora creado - {suscriptor}", 'info')
                    
            except Exception as e:
                registros_con_error += 1
                self.log(f"Error al procesar fila {idx+2}: {str(e)}", 'error')
                self.log(f"Datos: {row.to_dict()}", 'debug')
                
        return registros_creados, registros_con_error
    
    @transaction.atomic
    def import_particulares_sin_impresora(self, file_path, sheet_name=0):
        """
        Importa datos de particulares sin impresora desde un Excel.
        
        Args:
            file_path: Ruta al archivo Excel.
            sheet_name: Nombre o índice de la hoja a leer.
            
        Returns:
            Tuple: (registros_creados, registros_con_error)
        """
        df = self.read_excel(file_path, sheet_name)
        
        # Contadores para seguimiento
        registros_creados = 0
        registros_con_error = 0
        
        # Obtener los mapeos de columnas del ExcelMapper
        columnas_suscriptor = ExcelMapper.columnas_suscriptor_part_sin_imp()
        
        # Procesar cada fila del Excel
        for idx, row in df.iterrows():
            try:
                with transaction.atomic():
                    # Crear suscriptor
                    suscriptor_data = {}
                    for col_excel, campo_modelo in columnas_suscriptor.items():
                        if col_excel in row and pd.notna(row[col_excel]):
                            # Procesar campos especiales
                            if campo_modelo == 'telefono':
                                suscriptor_data[campo_modelo] = ExcelParser.clean_phone_number(row[col_excel])
                            elif campo_modelo == 'fecha_nacimiento':
                                suscriptor_data[campo_modelo] = ExcelParser.parse_date(row[col_excel])
                            else:
                                suscriptor_data[campo_modelo] = row[col_excel]
                    
                    # Añadir tipo suscriptor
                    suscriptor_data['tipo'] = 'particular'
                    
                    # Crear o actualizar suscriptor por email
                    email = suscriptor_data.get('email')
                    if not email:
                        self.log(f"Fila {idx+2} sin email, omitiendo", 'warning')
                        registros_con_error += 1
                        continue
                    
                    suscriptor, created = Suscriptor.objects.update_or_create(
                        email=email,
                        defaults=suscriptor_data
                    )
                    
                    # Crear relación particular sin impresora
                    ParticularSinImpresora.objects.update_or_create(
                        suscriptor=suscriptor
                    )
                    
                    registros_creados += 1
                    self.log(f"Fila {idx+2}: Particular sin impresora creado - {suscriptor}", 'info')
                    
            except Exception as e:
                registros_con_error += 1
                self.log(f"Error al procesar fila {idx+2}: {str(e)}", 'error')
                self.log(f"Datos: {row.to_dict()}", 'debug')
                
        return registros_creados, registros_con_error
    
    @transaction.atomic
    def import_instituciones_con_impresora(self, file_path, sheet_name=0):
        """
        Importa datos de instituciones con impresora desde un Excel.
        
        Args:
            file_path: Ruta al archivo Excel.
            sheet_name: Nombre o índice de la hoja a leer.
            
        Returns:
            Tuple: (registros_creados, registros_con_error)
        """
        df = self.read_excel(file_path, sheet_name)
        
        # Contadores para seguimiento
        registros_creados = 0
        registros_con_error = 0
        
        # Obtener los mapeos de columnas del ExcelMapper
        columnas_suscriptor = ExcelMapper.columnas_suscriptor_inst_con_imp()
        columnas_impresora = ExcelMapper.columnas_impresora_inst_con_imp()
        columnas_institucion = ExcelMapper.columnas_institucion_con_imp()
        
        # Procesar cada fila del Excel
        for idx, row in df.iterrows():
            try:
                with transaction.atomic():
                    # Crear suscriptor
                    suscriptor_data = {}
                    for col_excel, campo_modelo in columnas_suscriptor.items():
                        if col_excel in row and pd.notna(row[col_excel]):
                            # Procesar campos especiales de suscriptor
                            if campo_modelo == 'telefono':
                                suscriptor_data[campo_modelo] = ExcelParser.clean_phone_number(row[col_excel])
                            elif campo_modelo == 'fecha_nacimiento':
                                suscriptor_data[campo_modelo] = ExcelParser.parse_date(row[col_excel])
                            else:
                                suscriptor_data[campo_modelo] = row[col_excel]
                    
                    # Añadir tipo suscriptor y nombre para el campo requerido
                    suscriptor_data['tipo'] = 'institucion'
                    if 'nombre_institucion' in suscriptor_data:
                        suscriptor_data['nombre'] = suscriptor_data['nombre_institucion'][:100]  # Limitar a 100 chars
                    
                    # Crear o actualizar suscriptor por email
                    email = suscriptor_data.get('email')
                    if not email:
                        self.log(f"Fila {idx+2} sin email, omitiendo", 'warning')
                        registros_con_error += 1
                        continue
                    
                    suscriptor, created = Suscriptor.objects.update_or_create(
                        email=email,
                        defaults=suscriptor_data
                    )
                    
                    # Crear impresora
                    impresora_data = {}  
                    for col_excel, campo_modelo in columnas_impresora.items():
                        if col_excel in row and pd.notna(row[col_excel]):
                            # Procesar campos especiales de impresora
                            if campo_modelo == 'anios_experiencia':
                                impresora_data[campo_modelo] = ExcelParser.parse_years_experience(row[col_excel])
                            elif campo_modelo == 'cantidad_equipos':
                                impresora_data[campo_modelo] = ExcelParser.parse_equipment_count(row[col_excel])
                            else:
                                impresora_data[campo_modelo] = row[col_excel]
                    
                    impresora = Impresora.objects.create(**impresora_data)
                    
                    # Crear relación institución con impresora
                    institucion_data = {'impresora': impresora}
                    for col_excel, campo_modelo in columnas_institucion.items():
                        if col_excel in row and pd.notna(row[col_excel]):
                            institucion_data[campo_modelo] = row[col_excel]
                    
                    InstitucionConImpresora.objects.update_or_create(
                        suscriptor=suscriptor,
                        defaults=institucion_data
                    )
                    
                    registros_creados += 1
                    self.log(f"Fila {idx+2}: Institución con impresora creada - {suscriptor}", 'info')
                    
            except Exception as e:
                registros_con_error += 1
                self.log(f"Error al procesar fila {idx+2}: {str(e)}", 'error')
                self.log(f"Datos: {row.to_dict()}", 'debug')
                
        return registros_creados, registros_con_error
    
    @transaction.atomic
    def import_instituciones_sin_impresora(self, file_path, sheet_name=0):
        """
        Importa datos de instituciones sin impresora desde un Excel.
        
        Args:
            file_path: Ruta al archivo Excel.
            sheet_name: Nombre o índice de la hoja a leer.
            
        Returns:
            Tuple: (registros_creados, registros_con_error)
        """
        df = self.read_excel(file_path, sheet_name)
        
        # Contadores para seguimiento
        registros_creados = 0
        registros_con_error = 0
        
        # Obtener los mapeos de columnas del ExcelMapper
        columnas_suscriptor = ExcelMapper.columnas_suscriptor_inst_sin_imp()
        columnas_institucion = ExcelMapper.columnas_institucion_sin_imp()
        
        # Procesar cada fila del Excel
        for idx, row in df.iterrows():
            try:
                with transaction.atomic():
                    # Crear suscriptor
                    suscriptor_data = {}
                    for col_excel, campo_modelo in columnas_suscriptor.items():
                        if col_excel in row and pd.notna(row[col_excel]):
                            # Procesar campos especiales
                            if campo_modelo == 'telefono':
                                suscriptor_data[campo_modelo] = ExcelParser.clean_phone_number(row[col_excel])
                            elif campo_modelo == 'fecha_nacimiento':
                                suscriptor_data[campo_modelo] = ExcelParser.parse_date(row[col_excel])
                            else:
                                suscriptor_data[campo_modelo] = row[col_excel]
                    
                    # Añadir tipo suscriptor y nombre para el campo requerido
                    suscriptor_data['tipo'] = 'institucion'
                    if 'nombre_institucion' in suscriptor_data:
                        suscriptor_data['nombre'] = suscriptor_data['nombre_institucion'][:100]  # Limitar a 100 chars
                    
                    # Crear o actualizar suscriptor por email
                    email = suscriptor_data.get('email')
                    if not email:
                        self.log(f"Fila {idx+2} sin email, omitiendo", 'warning')
                        registros_con_error += 1
                        continue
                    
                    suscriptor, created = Suscriptor.objects.update_or_create(
                        email=email,
                        defaults=suscriptor_data
                    )
                    
                    # Crear relación institución sin impresora
                    institucion_data = {}
                    for col_excel, campo_modelo in columnas_institucion.items():
                        if col_excel in row and pd.notna(row[col_excel]):
                            institucion_data[campo_modelo] = row[col_excel]
                    
                    InstitucionSinImpresora.objects.update_or_create(
                        suscriptor=suscriptor,
                        defaults=institucion_data
                    )
                    
                    registros_creados += 1
                    self.log(f"Fila {idx+2}: Institución sin impresora creada - {suscriptor}", 'info')
                    
            except Exception as e:
                registros_con_error += 1
                self.log(f"Error al procesar fila {idx+2}: {str(e)}", 'error')
                self.log(f"Datos: {row.to_dict()}", 'debug')
                
        return registros_creados, registros_con_error
        
    @transaction.atomic
    def import_nodos_recepcion(self, file_path, sheet_name=0):
        """
        Importa datos de nodos de recepción desde un Excel.
        Si el suscriptor no existe, lo crea automáticamente.
        
        Args:
            file_path: Ruta al archivo Excel.
            sheet_name: Nombre o índice de la hoja a leer.
            
        Returns:
            Tuple: (registros_creados, registros_con_error)
        """
        df = self.read_excel(file_path, sheet_name)
        
        # Mostrar las columnas del Excel para debug
        self.log(f"Columnas en el Excel: {list(df.columns)}", 'info')
        
        # Contadores para seguimiento
        registros_creados = 0
        suscriptores_creados = 0
        registros_con_error = 0
        
        # Obtener los mapeos de columnas del ExcelMapper
        columnas_nodo = ExcelMapper.columnas_nodo_recepcion()
        
        # Columna que contiene el email y nombre del participante
        email_col = 'Correo electrónico:'
        nombre_participante_col = 'Nombre del participante particular o institución:'
        
        # Procesar cada fila del Excel
        for idx, row in df.iterrows():
            try:
                with transaction.atomic():
                    # Verificar si hay un email válido
                    if email_col not in df.columns or pd.isna(row[email_col]):
                        self.log(f"Fila {idx+2} sin columna de email o valor vacío, omitiendo", 'warning')
                        registros_con_error += 1
                        continue
                    
                    email_suscriptor = str(row[email_col]).strip()
                    
                    # Buscar suscriptor por email o crearlo si no existe
                    suscriptor = None
                    suscriptor_creado = False
                    
                    try:
                        suscriptor = Suscriptor.objects.get(email=email_suscriptor)
                    except Suscriptor.DoesNotExist:
                        # Obtener el nombre del participante para el nuevo suscriptor
                        nombre_participante = ""
                        if nombre_participante_col in df.columns and pd.notna(row[nombre_participante_col]):
                            nombre_participante = str(row[nombre_participante_col]).strip()
                        
                        # Crear un nuevo suscriptor con datos mínimos
                        suscriptor_data = {
                            'email': email_suscriptor,
                            'nombre': nombre_participante[:100],  # Limitar a 100 caracteres como máximo
                            'tipo': 'particular'  # Valor por defecto
                        }
                        
                        # Agregar más campos del nodo al suscriptor si están disponibles
                        if 'Teléfono:' in df.columns and pd.notna(row['Teléfono:']):
                            suscriptor_data['telefono'] = ExcelParser.clean_phone_number(row['Teléfono:'])
                        else:
                            suscriptor_data['telefono'] = '0000000000'  # Campo requerido
                        
                        if 'Calle:' in df.columns and pd.notna(row['Calle:']):
                            suscriptor_data['calle'] = row['Calle:']
                        else:
                            suscriptor_data['calle'] = 'Sin datos'  # Campo requerido
                        
                        if 'Numero:' in df.columns and pd.notna(row['Numero:']):
                            suscriptor_data['numero'] = row['Numero:']
                        else:
                            suscriptor_data['numero'] = 'S/N'  # Campo requerido
                        
                        if 'Codigo Postal:' in df.columns and pd.notna(row['Codigo Postal:']):
                            suscriptor_data['codigo_postal'] = row['Codigo Postal:']
                        else:
                            suscriptor_data['codigo_postal'] = '0000'  # Campo requerido
                        
                        if 'Localidad:' in df.columns and pd.notna(row['Localidad:']):
                            suscriptor_data['ciudad'] = row['Localidad:']
                        else:
                            suscriptor_data['ciudad'] = 'Sin datos'  # Campo requerido
                        
                        if 'Provincia:' in df.columns and pd.notna(row['Provincia:']):
                            suscriptor_data['provincia'] = row['Provincia:']
                        else:
                            suscriptor_data['provincia'] = 'Sin datos'  # Campo requerido
                        
                        # Crear el suscriptor
                        suscriptor = Suscriptor.objects.create(**suscriptor_data)
                        suscriptores_creados += 1
                        suscriptor_creado = True
                        self.log(f"Fila {idx+2}: Creado nuevo suscriptor con email {email_suscriptor}", 'info')
                    
                    # Preparar datos del nodo
                    nodo_data = {}
                    
                    # Procesar campos básicos
                    for col_excel, campo_modelo in columnas_nodo.items():
                        if col_excel in df.columns and pd.notna(row[col_excel]):
                            # Procesar campos especiales
                            if campo_modelo == 'telefono':
                                nodo_data[campo_modelo] = ExcelParser.clean_phone_number(row[col_excel])
                            elif campo_modelo == 'numero_orden' and not isinstance(row[col_excel], (int, float)):
                                # Intentar convertir a entero si no es un número
                                try:
                                    nodo_data[campo_modelo] = int(float(str(row[col_excel]).replace(',', '.')))
                                except (ValueError, TypeError):
                                    nodo_data[campo_modelo] = 0
                            else:
                                nodo_data[campo_modelo] = row[col_excel]
                    
                    # Procesar el campo nodo_seleccionado
                    if 'nodo_seleccionado' in nodo_data:
                        # Mapear el valor a uno de los valores aceptados
                        seleccion = str(nodo_data['nodo_seleccionado']).strip()
                        
                        if 'Ciudad de Buenos Aires' in seleccion:
                            nodo_data['nodo_seleccionado'] = 'CABA'
                            # Agregar detalles del nodo si existen
                            if 'Ciudad de Buenos Aires:' in df.columns and pd.notna(row['Ciudad de Buenos Aires:']):
                                nodo_data['detalles_nodo'] = str(row['Ciudad de Buenos Aires:'])
                        elif 'Gran Buenos Aires' in seleccion:
                            nodo_data['nodo_seleccionado'] = 'GBA'
                            if 'Gran Buenos Aires:' in df.columns and pd.notna(row['Gran Buenos Aires:']):
                                nodo_data['detalles_nodo'] = str(row['Gran Buenos Aires:'])
                        elif 'Provincia de Buenos Aires' in seleccion:
                            nodo_data['nodo_seleccionado'] = 'PBA'
                            if 'Provincia de Buenos Aires' in df.columns and pd.notna(row['Provincia de Buenos Aires']):
                                nodo_data['detalles_nodo'] = str(row['Provincia de Buenos Aires'])
                        elif 'Provincias Argentinas' in seleccion:
                            nodo_data['nodo_seleccionado'] = 'PA'
                            if 'Provincias Argentinas' in df.columns and pd.notna(row['Provincias Argentinas']):
                                nodo_data['detalles_nodo'] = str(row['Provincias Argentinas'])
                        else:
                            # Usar un valor predeterminado según la provincia
                            provincia = nodo_data.get('provincia', '').strip().upper()
                            if provincia == 'CABA' or provincia == 'CIUDAD DE BUENOS AIRES':
                                nodo_data['nodo_seleccionado'] = 'CABA'
                            elif provincia == 'BUENOS AIRES':
                                nodo_data['nodo_seleccionado'] = 'PBA'
                            else:
                                nodo_data['nodo_seleccionado'] = 'PA'
                    else:
                        # Si no hay valor de nodo_seleccionado, inferirlo de la provincia
                        provincia = nodo_data.get('provincia', '').strip().upper()
                        if provincia == 'CABA' or provincia == 'CIUDAD DE BUENOS AIRES':
                            nodo_data['nodo_seleccionado'] = 'CABA'
                        elif provincia == 'BUENOS AIRES':
                            nodo_data['nodo_seleccionado'] = 'PBA'
                        else:
                            nodo_data['nodo_seleccionado'] = 'PA'
                    
                    # Agregar suscriptor al nodo
                    nodo_data['suscriptor'] = suscriptor
                    
                    # Asegurar que los campos obligatorios tienen valores
                    if 'numero_bloque' not in nodo_data or not nodo_data['numero_bloque']:
                        # Generar un valor predeterminado para numero_bloque si es necesario
                        nodo_data['numero_bloque'] = f"NO-BLOQUE-{idx+1}"
                        self.log(f"Fila {idx+2}: Número de bloque faltante, asignando valor predeterminado", 'warning')
                    
                    if 'numero_orden' not in nodo_data:
                        nodo_data['numero_orden'] = idx + 1
                    
                    # Crear o actualizar nodo
                    # Si ya existe un nodo con la misma combinación de suscriptor y número de bloque, se actualiza
                    try:
                        nodo, created = NodoRecepcion.objects.update_or_create(
                            suscriptor=suscriptor,
                            numero_bloque=nodo_data.get('numero_bloque', ''),
                            defaults=nodo_data
                        )
                        
                        registros_creados += 1
                        self.log(f"Fila {idx+2}: Nodo de recepción {'creado' if created else 'actualizado'} - {nodo}", 'info')
                    except Exception as e:
                        self.log(f"Error al crear/actualizar nodo para fila {idx+2}: {str(e)}", 'error')
                        self.log(f"Datos del nodo: {nodo_data}", 'debug')
                        registros_con_error += 1
                        
                        # Si se creó un suscriptor pero falló la creación del nodo, eliminar el suscriptor para evitar huérfanos
                        if suscriptor_creado:
                            suscriptor.delete()
                            suscriptores_creados -= 1
                            self.log(f"Eliminado suscriptor creado (email: {email_suscriptor}) debido a error en nodo", 'warning')
                    
            except Exception as e:
                registros_con_error += 1
                self.log(f"Error al procesar fila {idx+2}: {str(e)}", 'error')
                self.log(f"Datos: {row.to_dict()}", 'debug')
                    
        self.log(f"Total de suscriptores creados automáticamente: {suscriptores_creados}", 'info')
        return registros_creados, registros_con_error
    
    #El excel mas importante, el de los bloques y participantes
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
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        self.log(f"Archivo leído correctamente. Dimensiones: {df.shape}", 'info')
        
        # Contadores para seguimiento
        bloques_creados = 0
        bloques_actualizados = 0
        bloques_con_error = 0
        estados_count = {'libre': 0, 'asignado': 0, 'validacion': 0, 'entregado_nodo': 0, 'recibido_m3d': 0, 'diploma_entregado': 0}
        
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
        col_diploma = find_column(['diploma', 'ok'])
        
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
        from django.utils import timezone
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