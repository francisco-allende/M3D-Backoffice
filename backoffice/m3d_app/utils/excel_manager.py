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
    
    @transaction.atomic
    def import_bloques_participantes(self, file_path, sheet_name=0):
        """
        Importa datos de bloques y su asignación a suscriptores desde Excel.
        
        Args:
            file_path: Ruta al archivo Excel.
            sheet_name: Nombre o índice de la hoja a leer.
            
        Returns:
            Tuple: (bloques_creados, bloques_actualizados, bloques_con_error)
        """
        # Leer Excel sin encabezados, usando posiciones numéricas
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        self.log(f"Archivo leído correctamente. Dimensiones: {df.shape}", 'info')
        
        # Contadores para seguimiento
        bloques_creados = 0
        bloques_actualizados = 0
        bloques_con_error = 0
        
        # Índices de columnas relevantes (ajustar según la estructura real del Excel)
        COL_ID = 0           # Primera columna (número/ID)
        COL_PREFIJO = 1      # Segunda columna (M3D)
        COL_BLOQUE = 2       # Tercera columna (número de bloque)
        COL_EMAIL = 3        # Columna con email del suscriptor
        COL_VALIDACION = 12  # Columna con estado de foto de validación
        COL_ENTREGADO = 13   # Columna con estado de entregado en nodo
        COL_RECIBIDO = 14    # Columna con estado de recibido en M3D
        COL_DIPLOMA = 15     # Columna con estado de diploma entregado
        
        # La última institución procesada y sus bloques
        ultima_institucion_email = None
        bloques_institucion = []
        
        # Fecha actual para campos de fecha
        from django.utils import timezone
        now = timezone.now()
        
        # Imprimir primeras filas para debug
        self.log(f"Primeras 3 filas del Excel: {df.head(3)}", 'info')
        
        # Procesar cada fila del Excel
        for idx, row in df.iterrows():
            try:
                # Saltear primera fila si contiene encabezados
                if idx == 0 and isinstance(row[COL_BLOQUE], str) and not row[COL_BLOQUE].strip().startswith(('0', '1', '2', '3', '4', '5', '6')):
                    self.log("Saltando primera fila (encabezados)", 'info')
                    continue
                    
                with transaction.atomic():
                    # Obtener número de bloque
                    if COL_BLOQUE >= len(row) or pd.isna(row[COL_BLOQUE]):
                        self.log(f"Fila {idx+1}: No hay número de bloque, omitiendo", 'warning')
                        continue
                        
                    numero_bloque = str(row[COL_BLOQUE]).strip()
                    if not numero_bloque or numero_bloque.lower() == 'nan':
                        self.log(f"Fila {idx+1}: Número de bloque vacío, omitiendo", 'warning')
                        continue
                    
                    # Obtener email del suscriptor
                    email_suscriptor = None
                    if COL_EMAIL < len(row) and not pd.isna(row[COL_EMAIL]):
                        email_suscriptor = str(row[COL_EMAIL]).strip()
                    
                    # Si es una fila vacía de una institución (que tiene 3 bloques)
                    if not email_suscriptor or email_suscriptor.lower() == 'nan':
                        # Si ya procesamos una institución, podría ser uno de sus bloques adicionales
                        if ultima_institucion_email and len(bloques_institucion) < 3:
                            self.log(f"Fila {idx+1}: Asignando bloque adicional a la institución con email {ultima_institucion_email}", 'info')
                            email_suscriptor = ultima_institucion_email
                        else:
                            # Si no hay email y no pertenece a una institución ya procesada, es un bloque libre
                            self.log(f"Fila {idx+1}: No hay email, bloque libre", 'info')
                            suscriptor = None
                            estado = 'libre'
                            nodo_recepcion = None
                    else:
                        # Buscar el suscriptor por email
                        try:
                            suscriptor = Suscriptor.objects.get(email=email_suscriptor)
                            
                            # Verificar si es una institución
                            if suscriptor.tipo == 'institucion':
                                ultima_institucion_email = email_suscriptor
                                bloques_institucion.append(numero_bloque)
                                self.log(f"Fila {idx+1}: Institución encontrada, email={email_suscriptor}, bloques={bloques_institucion}", 'info')
                            else:
                                # Si es un particular, reiniciamos el seguimiento de instituciones
                                ultima_institucion_email = None
                                bloques_institucion = []
                            
                            # Buscar el nodo asociado al suscriptor (si existe)
                            nodo_recepcion = NodoRecepcion.objects.filter(suscriptor=suscriptor).first()
                            
                            # Si hay suscriptor, el estado mínimo es 'asignado'
                            estado = 'asignado'
                        except Suscriptor.DoesNotExist:
                            self.log(f"Fila {idx+1}: No se encontró suscriptor con email {email_suscriptor}", 'warning')
                            suscriptor = None
                            estado = 'libre'
                            nodo_recepcion = None
                    
                    # CORRECCIÓN: Solo procesar estados si hay un suscriptor válido
                    
                    if suscriptor:
                        # Determinar el estado del bloque basado en las columnas de estado
                        # Primero, vamos a imprimir los valores para diagnóstico
                        self.log(f"Fila {idx+1}: Valores de estado - "
                                f"VALIDA FOTO: {row[COL_VALIDACION] if COL_VALIDACION < len(row) else 'NA'}, "
                                f"anoto nodo: {row[COL_ENTREGADO] if COL_ENTREGADO < len(row) else 'NA'}, "
                                f"RECIBIMOS: {row[COL_RECIBIDO] if COL_RECIBIDO < len(row) else 'NA'}, "
                                f"Diploma OK: {row[COL_DIPLOMA] if COL_DIPLOMA < len(row) else 'NA'}", 'info')
                        
                        # Vamos a usar una lógica mejorada para detectar estados
                        estados = []
                        
                        # Para el diploma, vamos a aceptar prácticamente cualquier valor no nulo y que no sea explícitamente negativo
                        if COL_DIPLOMA < len(row) and not pd.isna(row[COL_DIPLOMA]):
                            valor_diploma = str(row[COL_DIPLOMA]).strip().lower()
                            if valor_diploma and valor_diploma not in ['0', 'nan', 'false', 'no']:
                                estados.append('diploma_entregado')
                        
                        # Para recibidos, igual
                        if COL_RECIBIDO < len(row) and not pd.isna(row[COL_RECIBIDO]):
                            valor_recibido = str(row[COL_RECIBIDO]).strip().lower()
                            if valor_recibido and valor_recibido not in ['0', 'nan', 'false', 'no']:
                                estados.append('recibido_m3d')
                        
                        # Para entregado en nodo
                        if COL_ENTREGADO < len(row) and not pd.isna(row[COL_ENTREGADO]):
                            valor_entregado = str(row[COL_ENTREGADO]).strip().lower()
                            if valor_entregado and valor_entregado not in ['0', 'nan', 'false', 'no']:
                                estados.append('entregado_nodo')
                        
                        # Para validación
                        if COL_VALIDACION < len(row) and not pd.isna(row[COL_VALIDACION]):
                            valor_validacion = str(row[COL_VALIDACION]).strip().lower()
                            if valor_validacion and valor_validacion not in ['0', 'nan', 'false', 'no']:
                                estados.append('validacion')
                        
                        # Seleccionar el estado más avanzado si existe
                        if estados:
                            # Orden de prioridad: diploma_entregado > recibido_m3d > entregado_nodo > validacion > asignado > libre
                            orden_estados = ['libre', 'asignado', 'validacion', 'entregado_nodo', 'recibido_m3d', 'diploma_entregado']
                            estado = max(estados, key=lambda x: orden_estados.index(x))
                        
                        # Logging para diagnóstico
                        self.log(f"Fila {idx+1}: Estados detectados: {estados}, estado final: {estado}", 'debug')




                    # Preparar datos del bloque
                    bloque_data = {
                        'numero_bloque': numero_bloque,
                        'suscriptor': suscriptor,
                        'nodo_recepcion': nodo_recepcion,
                        'estado': estado
                    }
                    
                    # Establecer fechas según el estado
                    if estado != 'libre':
                        bloque_data['fecha_asignacion'] = now
                    if estado in ['validacion', 'entregado_nodo', 'recibido_m3d', 'diploma_entregado']:
                        bloque_data['fecha_validacion'] = now
                    if estado in ['entregado_nodo', 'recibido_m3d', 'diploma_entregado']:
                        bloque_data['fecha_entrega_nodo'] = now
                    if estado in ['recibido_m3d', 'diploma_entregado']:
                        bloque_data['fecha_recepcion_m3d'] = now
                    if estado == 'diploma_entregado':
                        bloque_data['fecha_entrega_diploma'] = now
                    
                    # Crear o actualizar el bloque
                    try:
                        bloque, created = Bloque.objects.update_or_create(
                            numero_bloque=numero_bloque,
                            defaults=bloque_data
                        )
                        
                        if created:
                            bloques_creados += 1
                            self.log(f"Fila {idx+1}: Bloque {numero_bloque} creado con estado {estado}", 'info')
                        else:
                            bloques_actualizados += 1
                            self.log(f"Fila {idx+1}: Bloque {numero_bloque} actualizado con estado {estado}", 'info')
                        
                    except Exception as e:
                        bloques_con_error += 1
                        self.log(f"Error al crear/actualizar bloque {numero_bloque}: {str(e)}", 'error')
                    
            except Exception as e:
                bloques_con_error += 1
                self.log(f"Error al procesar fila {idx+1}: {str(e)}", 'error')
                self.log(f"Datos de la fila: {row.to_dict() if hasattr(row, 'to_dict') else list(row)}", 'debug')
        
        self.log(f"Importación completada: {bloques_creados} bloques creados, {bloques_actualizados} bloques actualizados, {bloques_con_error} bloques con error", 'info')
        return bloques_creados, bloques_actualizados, bloques_con_error