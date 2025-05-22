
class ExcelMapper:
    @staticmethod
    def columnas_suscriptor():
        return {
            'Nombre y Apellido: Nombre': 'nombre',
            'Nombre y Apellido: Apellidos': 'apellido',
            'Correo electrónico': 'email',
            'Teléfono': 'telefono',
            'Calle': 'calle',
            'Nro': 'numero',
            'Piso y Depto': 'piso_depto',
            'Codigo Postal': 'codigo_postal',
            'Ciudad': 'ciudad',
            'Provincia': 'provincia',
            'Fecha de nacimiento': 'fecha_nacimiento',
            'DNI': 'dni',
            '¿Como te enteraste del proyecto?': 'como_se_entero',
            '¿Porque queres participar de Malvinas 3D?': 'motivo_participacion'
        }
    
    @staticmethod
    def columnas_impresora():
        return {
            '¿Cuántos años hace que trabajás con esta tecnología?': 'anios_experiencia',
            '¿De qué Marcas y Modelos son tus equipos?': 'marcas_modelos_equipos',
            '¿Qué materiales usás regularmente?': 'materiales_uso',
            '¿Cuántos equipos tenés?': 'cantidad_equipos',
            '¿Cuál es la dimensión máxima qué podés imprimir?': 'dimension_maxima_impresion',
            '¿Qué Software usás?': 'software_uso'
        }
    
    # 1. Mapeo para particulares con impresora (formparticularesconimpresora.xlsx)
    # ---------------------------------------------------------
    @staticmethod
    def columnas_suscriptor_part_con_imp():
        return {
            'Nombre y Apellido: Nombre': 'nombre',
            'Nombre y Apellido: Apellidos': 'apellido',
            'Correo electrónico': 'email',
            'Teléfono': 'telefono',
            'Calle': 'calle',
            'Nro': 'numero',
            'Piso y Depto': 'piso_depto',
            'Codigo Postal': 'codigo_postal',
            'Ciudad': 'ciudad',
            'Provincia': 'provincia',
            'Fecha de nacimiento': 'fecha_nacimiento',
            'DNI': 'dni',
            '¿Como te enteraste del proyecto?': 'como_se_entero',
            '¿Porque queres participar de Malvinas 3D?': 'motivo_participacion'
        }
    
    @staticmethod
    def columnas_impresora_part_con_imp():
        return {
            '¿Cuántos años hace que trabajás con esta tecnología?': 'anios_experiencia',
            '¿De qué Marcas y Modelos son tus equipos?': 'marcas_modelos_equipos',
            '¿Qué materiales usás regularmente?': 'materiales_uso',
            '¿Cuántos equipos tenés?': 'cantidad_equipos',
            '¿Cuál es la dimensión máxima qué podés imprimir?': 'dimension_maxima_impresion',
            '¿Qué Software usás?': 'software_uso'
        }

    # 2. Mapeo para particulares sin impresora (formparticularessinimpresora.xlsx)
    # ---------------------------------------------------------
    @staticmethod
    def columnas_suscriptor_part_sin_imp():
        return {
            'Nombre y Apellido: Nombre': 'nombre',
            'Nombre y Apellido: Apellidos': 'apellido',
            'Correo electrónico': 'email',
            'Teléfono': 'telefono',
            'Calle': 'calle',
            'Nro': 'numero',
            'Piso y Depto': 'piso_depto',
            'Codigo Postal': 'codigo_postal',
            'Ciudad': 'ciudad',
            'Provincia': 'provincia',
            'Fecha de nacimiento': 'fecha_nacimiento',
            'DNI': 'dni',
            '¿Como te enteraste del proyecto?': 'como_se_entero',
            '¿Porque queres participar de Malvinas 3D?': 'motivo_participacion'
        }

    # 3. Mapeo para instituciones con impresora (forminstitucionesconimpresora.xlsx)
    # ---------------------------------------------------------
    @staticmethod
    def columnas_suscriptor_inst_con_imp():
        return {
            'Nombre de la Institución': 'nombre_institucion',
            'Correo electrónico': 'email',
            'Teléfono': 'telefono',
            'Calle': 'calle',
            'Nro': 'numero',
            'Piso y Depto': 'piso_depto',
            'Codigo Postal': 'codigo_postal',
            'Ciudad': 'ciudad',
            'Provincia': 'provincia',
            '¿Como te enteraste del proyecto?': 'como_se_entero',
            '¿Porque querés participar de MALVINAS 3D?': 'motivo_participacion'
        }
    @staticmethod
    def columnas_impresora_inst_con_imp():
        return {
        '¿Cuántos años hace que trabajás con esta tecnología?': 'anios_experiencia',
        '¿De qué Marcas y Modelos son tus equipos?': 'marcas_modelos_equipos',
        '¿Qué materiales usás regularmente?': 'materiales_uso',
        '¿Cuántos equipos tenés?': 'cantidad_equipos',
        '¿Cuál es la dimensión máxima qué podés imprimir?': 'dimension_maxima_impresion',
        '¿Qué Software usás?': 'software_uso'
    }

    @staticmethod
    def columnas_institucion_con_imp():  
        return {
        'Nombre y Apellido del responsable': 'nombre_responsable',
        'DNI': 'dni_responsable'
    }

    # 4. Mapeo para instituciones sin impresora (forminstitucionessinimpresora.xlsx)
    # ---------------------------------------------------------
    @staticmethod
    def columnas_suscriptor_inst_sin_imp(): 
        return {
        'Nombre de la Institución': 'nombre_institucion',
        'Correo electrónico': 'email',
        'Teléfono': 'telefono',
        'Calle': 'calle',
        'Nro': 'numero',
        'Piso y Depto': 'piso_depto',
        'Codigo Postal': 'codigo_postal',
        'Ciudad': 'ciudad',
        'Provincia': 'provincia',
        '¿Como te enteraste del proyecto?': 'como_se_entero',
        '¿Porque queres participar de Malvinas 3D?': 'motivo_participacion'
    }

    @staticmethod
    def columnas_institucion_sin_imp(): 
        return {
        'Nombre y Apellido del responsable': 'nombre_responsable',
        'DNI': 'dni_responsable'
    }

    # 5. Mapeo para nodos de recepcion (nodosrecepcion.xlsx)
    # ---------------------------------------------------------
    @staticmethod
    def columnas_nodo_recepcion():
        """
        Mapeo de columnas para el archivo de nodos de recepción.
        Basado en los nombres exactos de columnas del Excel, excluyendo campos no existentes en el modelo.
        """
        return {
            'Número/s de orden de 4 cifras:': 'numero_orden',
            'Numero/s de bloque/s de 2 cifras:': 'numero_bloque',
            # Excluimos 'Nombre del participante particular o institución:' ya que no existe en el modelo
            'Nombre del responsable de impresión 3d:': 'responsable_impresion',
            'Calle:': 'calle',
            'Numero:': 'numero',
            'Codigo Postal:': 'codigo_postal',
            'Localidad:': 'localidad',
            'Departamento:': 'departamento',
            'Provincia:': 'provincia',
            'Teléfono:': 'telefono',
            'Correo electrónico:': 'email',
            'Seleccionar Nodo:': 'nodo_seleccionado'
        }
    
    
    # 6. Mapeo para bloques (PARTICIPANTESMALVINAS3D.xlsx)
    # ---------------------------------------------------------
    # Añadir a m3d_app/utils/excel_mapper.py

    @staticmethod
    def columnas_bloque_participantes():
        return {
            'N sorteo': 'nro_sorteo',                # Primera columna con números de identificación
            'prefijo': 'prefijo_m3d',            # Columna con "M3D"
            'bloque': 'numero_bloque',           # Columna con número de bloque (ej: "10-12")
            'MAIL': 'email_suscriptor',            # Email para relacionar con el suscriptor
            'VALIDA FOTO': 'estado_validacion',
            'anoto nodo': 'estado_entregado_nodo',
            'RECIBIMOS': 'estado_recibido_m3d',
            'Diploma OK': 'estado_diploma_entregado'
        }
    
    