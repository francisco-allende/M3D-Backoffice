from django.db import transaction
import pandas as pd
from .base import ExcelManagerBase
from m3d_app.models.suscriptor.suscriptor import Suscriptor
from m3d_app.models.impresora.impresora import Impresora
from m3d_app.models.suscriptor.particular_con_impresora import ParticularConImpresora
from m3d_app.models.suscriptor.particular_sin_impresora import ParticularSinImpresora
from m3d_app.models.suscriptor.institucion_con_impresora import InstitucionConImpresora
from m3d_app.models.suscriptor.institucion_sin_impresora import InstitucionSinImpresora
from m3d_app.utils.excel_mapper import ExcelMapper
from m3d_app.utils.excel_parser import ExcelParser

class ExcelManagerForSubs(ExcelManagerBase):
    """
    Gestor de Excel especializado en la importación de suscriptores.
    """
    
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