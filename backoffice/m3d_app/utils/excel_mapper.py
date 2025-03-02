
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

    @staticmethod
    def columnas_nodo_recepcion():
        return {
            'Orden': 'numero_orden',
            'Bloque': 'numero_bloque',
            'Responsable de impresión': 'responsable_impresion',
            'Calle': 'calle',
            'Número': 'numero',
            'CP': 'codigo_postal',
            'Localidad': 'localidad',
            'Departamento': 'departamento',
            'Provincia': 'provincia',
            'Teléfono': 'telefono',
            'Email': 'email',
            'Nodo seleccionado': 'nodo_seleccionado',
            'Detalles sobre el nodo': 'detalles_nodo'
        }