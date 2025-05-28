# En m3d_app/admin.py - Actualizar para aprovechar Jazzmin

from django.contrib import admin
from .models.suscriptor.suscriptor import Suscriptor 
from .models.suscriptor.institucion_con_impresora import InstitucionConImpresora
from .models.suscriptor.institucion_sin_impresora import InstitucionSinImpresora
from .models.suscriptor.particular_con_impresora import ParticularConImpresora
from .models.suscriptor.particular_sin_impresora import ParticularSinImpresora
from .models.nodos.nodo_recepcion import NodoRecepcion
from .models.impresora.impresora import Impresora
from .models.bloque3d.bloque import Bloque
import pandas as pd
from io import BytesIO
from django.http import HttpResponse

# Clase para mejorar la visualización de Bloques en el admin
class BloqueAdmin(admin.ModelAdmin):
    list_display = ('nro_sorteo', 'numero_bloque_display', 'seccion', 'numero', 'suscriptor', 'estado', 'fecha_asignacion')
    list_filter = ('seccion', 'estado')
    search_fields = ('nro_sorteo', 'numero_bloque', 'seccion', 'numero', 'suscriptor__nombre', 'suscriptor__nombre_institucion')
    readonly_fields = ('seccion', 'numero')
    date_hierarchy = 'fecha_asignacion'
    list_per_page = 20

    actions = ['exportar_excel']
    
    # Para mejorar la apariencia en Jazzmin
    list_display_links = ('numero_bloque_display',)

    def numero_bloque_display(self, obj):
        """
        Muestra el número de bloque con la leyenda (sin impresora) para secciones 32, 33 y 34
        """
        if obj.seccion == '*32' or obj.seccion == '*33' or obj.seccion == '*34':
            return f"{obj.numero_bloque} (sin impresora)"
        return obj.numero_bloque
    
    numero_bloque_display.short_description = 'Numero bloque'
    numero_bloque_display.admin_order_field = 'numero_bloque'

    def exportar_excel(self, request, queryset):
        """
        Exporta los bloques seleccionados (o todos) a Excel
        """
        # Si no hay selección, usar todos los bloques
        if not queryset:
            queryset = self.get_queryset(request)
        
        # Preparar los datos para el Excel
        data = []
        for bloque in queryset.select_related('suscriptor', 'nodo_recepcion'):
            # Obtener email del suscriptor
            email_suscriptor = bloque.suscriptor.email if bloque.suscriptor else ''
            
            # Determinar estados binarios (1 o 0) según el estado actual
            validacion = 1 if bloque.estado in ['validacion', 'entregado_nodo', 'recibido_m3d', 'diploma_entregado'] else 0
            entregado_nodo = 1 if bloque.estado in ['entregado_nodo', 'recibido_m3d', 'diploma_entregado'] else 0
            recibido_m3d = 1 if bloque.estado in ['recibido_m3d', 'diploma_entregado'] else 0
            diploma_entregado = 1 if bloque.estado == 'diploma_entregado' else 0
            
            # Obtener información del suscriptor
            nombre_suscriptor = ''
            if bloque.suscriptor:
                if bloque.suscriptor.tipo == 'institucion':
                    nombre_suscriptor = bloque.suscriptor.nombre_institucion or bloque.suscriptor.nombre
                else:
                    apellido = bloque.suscriptor.apellido or ''
                    nombre_suscriptor = f"{bloque.suscriptor.nombre} {apellido}".strip()
            
            # Información adicional del suscriptor
            telefono = bloque.suscriptor.telefono if bloque.suscriptor else ''
            direccion = ''
            if bloque.suscriptor:
                partes_direccion = [
                    bloque.suscriptor.calle,
                    bloque.suscriptor.numero,
                    bloque.suscriptor.piso_depto,
                    bloque.suscriptor.ciudad,
                    bloque.suscriptor.provincia
                ]
                direccion = ', '.join([parte for parte in partes_direccion if parte])
            
            provincia = bloque.suscriptor.provincia if bloque.suscriptor else ''
            codigo_postal = bloque.suscriptor.codigo_postal if bloque.suscriptor else ''
            
            # Crear fila de datos
            fila = {
                'N sorteo': bloque.nro_sorteo or '',
                'prefijo': 'M3D',  # Siempre M3D
                'bloque': bloque.numero_bloque,
                'MAIL': email_suscriptor,
                'NOMBRE': nombre_suscriptor,
                'Telefono': telefono,
                'Direccion': direccion,
                'Provincia': provincia,
                'Codigo Postal': codigo_postal,
                'Estado Bloque': bloque.estado,
                'Fecha Asignacion': bloque.fecha_asignacion.strftime('%Y-%m-%d %H:%M:%S') if bloque.fecha_asignacion else '',
                'VALIDA FOTO': validacion,
                'anoto nodo': entregado_nodo,
                'RECIBIMOS': recibido_m3d,
                'Diploma OK': diploma_entregado,
            }
            data.append(fila)
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Crear el archivo Excel en memoria
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Bloques', index=False)
        
        # Preparar la respuesta HTTP
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="bloques_malvinas3d.xlsx"'
        
        return response
    
    exportar_excel.short_description = "Exportar bloques seleccionados a Excel"
    
    
    # Fieldsets para organizar la información en pestañas
    fieldsets = [
        ('Información del Bloque', {'fields': ['nro_sorteo', 'numero_bloque', 'seccion', 'numero', 'suscriptor', 'estado']}),
        ('Fechas', {'fields': ['fecha_asignacion', 'fecha_validacion', 'fecha_entrega_nodo', 'fecha_recepcion_m3d', 'fecha_entrega_diploma']}),
        ('Otros Datos', {'fields': ['nodo_recepcion', 'historia_asociada']}),
    ]

    def changelist_view(self, request, extra_context=None):
        """
        Personalizar la vista de lista para agregar botón de exportar todo
        """
        extra_context = extra_context or {}
        extra_context['has_export_button'] = True
        return super().changelist_view(request, extra_context)
    
    def get_urls(self):
        """
        Agregar URL personalizada para exportar todos los bloques
        """
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('exportar-todos/', self.admin_site.admin_view(self.exportar_todos_view), name='m3d_app_bloque_exportar_todos'),
        ]
        return custom_urls + urls
    
    def exportar_todos_view(self, request):
        """
        Vista para exportar todos los bloques
        """
        todos_los_bloques = self.get_queryset(request)
        return self.exportar_excel(request, todos_los_bloques)

# Clase para la visualización de Suscriptor con sus bloques
class SuscriptorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'nombre_institucion', 'email', 'tipo', 'telefono', 'provincia', 'get_bloques_count')
    list_filter = ('tipo', 'provincia', 'contactado')
    search_fields = ('nombre', 'apellido', 'nombre_institucion', 'email', 'telefono')
    list_per_page = 20

    actions = ['exportar_excel']
    
    def get_bloques_count(self, obj):
        return obj.bloques.count()
    get_bloques_count.short_description = 'Bloques'

    def exportar_excel(self, request, queryset):
        """
        Exporta los suscriptores seleccionados (o todos) a Excel
        """
        # Si no hay selección, usar todos los suscriptores
        if not queryset:
            queryset = self.get_queryset(request)
        
        # Preparar los datos para el Excel
        data = []
        for suscriptor in queryset.prefetch_related('bloques', 'particular_con_impresora__impresora', 'particular_sin_impresora', 'institucion_con_impresora__impresora', 'institucion_sin_impresora'):
            
            # Datos básicos del suscriptor
            fila = {
                'ID': suscriptor.id,
                'Tipo': suscriptor.tipo.title(),
                'Email': suscriptor.email,
                'Teléfono': suscriptor.telefono,
                'Fecha Registro': suscriptor.fecha_registro.strftime('%Y-%m-%d %H:%M:%S'),
                'Contactado': 'Sí' if suscriptor.contactado else 'No',
                'Foto Validada': 'Sí' if suscriptor.foto_validada else 'No',
                'Diploma Entregado': 'Sí' if suscriptor.diploma_entregado else 'No',
                
                # Dirección
                'Calle': suscriptor.calle,
                'Número': suscriptor.numero,
                'Piso/Depto': suscriptor.piso_depto or '',
                'Código Postal': suscriptor.codigo_postal,
                'Ciudad': suscriptor.ciudad,
                'Provincia': suscriptor.provincia,
                
                # Otros datos
                'Como se enteró': suscriptor.como_se_entero or '',
                'Motivo participación': suscriptor.motivo_participacion or '',
            }
            
            # Datos específicos según el tipo
            if suscriptor.tipo == 'particular':
                fila.update({
                    'Nombre': suscriptor.nombre,
                    'Apellido': suscriptor.apellido or '',
                    'Nombre Institución': '',
                    'DNI': suscriptor.dni or '',
                    'Fecha Nacimiento': suscriptor.fecha_nacimiento.strftime('%Y-%m-%d') if suscriptor.fecha_nacimiento else '',
                    'Nombre Responsable': '',
                    'DNI Responsable': '',
                })
                
                # Verificar si tiene impresora
                if hasattr(suscriptor, 'particular_con_impresora') and suscriptor.particular_con_impresora:
                    fila['Tiene Impresora'] = 'Sí'
                    impresora = suscriptor.particular_con_impresora.impresora
                    if impresora:
                        fila.update({
                            'Años Experiencia': impresora.anios_experiencia or '',
                            'Marcas y Modelos': impresora.marcas_modelos_equipos or '',
                            'Materiales Uso': impresora.materiales_uso or '',
                            'Cantidad Equipos': impresora.cantidad_equipos or '',
                            'Dimensión Máxima': impresora.dimension_maxima_impresion or '',
                            'Software Uso': impresora.software_uso or '',
                        })
                else:
                    fila['Tiene Impresora'] = 'No'
                    fila.update({
                        'Años Experiencia': '',
                        'Marcas y Modelos': '',
                        'Materiales Uso': '',
                        'Cantidad Equipos': '',
                        'Dimensión Máxima': '',
                        'Software Uso': '',
                    })
                    
            else:  # institución
                fila.update({
                    'Nombre': suscriptor.nombre,
                    'Apellido': '',
                    'Nombre Institución': suscriptor.nombre_institucion or '',
                    'DNI': '',
                    'Fecha Nacimiento': '',
                })
                
                # Datos del responsable
                if hasattr(suscriptor, 'institucion_con_impresora') and suscriptor.institucion_con_impresora:
                    fila['Tiene Impresora'] = 'Sí'
                    fila.update({
                        'Nombre Responsable': suscriptor.institucion_con_impresora.nombre_responsable or '',
                        'DNI Responsable': suscriptor.institucion_con_impresora.dni_responsable or '',
                    })
                    impresora = suscriptor.institucion_con_impresora.impresora
                    if impresora:
                        fila.update({
                            'Años Experiencia': impresora.anios_experiencia or '',
                            'Marcas y Modelos': impresora.marcas_modelos_equipos or '',
                            'Materiales Uso': impresora.materiales_uso or '',
                            'Cantidad Equipos': impresora.cantidad_equipos or '',
                            'Dimensión Máxima': impresora.dimension_maxima_impresion or '',
                            'Software Uso': impresora.software_uso or '',
                        })
                elif hasattr(suscriptor, 'institucion_sin_impresora') and suscriptor.institucion_sin_impresora:
                    fila['Tiene Impresora'] = 'No'
                    fila.update({
                        'Nombre Responsable': suscriptor.institucion_sin_impresora.nombre_responsable or '',
                        'DNI Responsable': suscriptor.institucion_sin_impresora.dni_responsable or '',
                        'Años Experiencia': '',
                        'Marcas y Modelos': '',
                        'Materiales Uso': '',
                        'Cantidad Equipos': '',
                        'Dimensión Máxima': '',
                        'Software Uso': '',
                    })
            
            # Información de bloques asignados
            bloques = suscriptor.bloques.all()
            bloques_info = []
            for bloque in bloques:
                bloques_info.append(f"{bloque.numero_bloque} ({bloque.estado})")
            
            fila['Bloques Asignados'] = '; '.join(bloques_info) if bloques_info else 'Ninguno'
            fila['Cantidad Bloques'] = len(bloques_info)
            
            data.append(fila)
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Reordenar columnas para que sea más lógico
        column_order = [
            'ID', 'Tipo', 'Nombre', 'Apellido', 'Nombre Institución', 'Email', 'Teléfono',
            'DNI', 'Fecha Nacimiento', 'Nombre Responsable', 'DNI Responsable',
            'Calle', 'Número', 'Piso/Depto', 'Código Postal', 'Ciudad', 'Provincia',
            'Tiene Impresora', 'Años Experiencia', 'Marcas y Modelos', 'Materiales Uso',
            'Cantidad Equipos', 'Dimensión Máxima', 'Software Uso',
            'Como se enteró', 'Motivo participación',
            'Cantidad Bloques', 'Bloques Asignados',
            'Contactado', 'Foto Validada', 'Diploma Entregado', 'Fecha Registro'
        ]
        
        # Reordenar y asegurar que todas las columnas existan
        for col in column_order:
            if col not in df.columns:
                df[col] = ''
        
        df = df[column_order]
        
        # Crear el archivo Excel en memoria
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Suscriptores', index=False)
            
            # Ajustar ancho de columnas
            worksheet = writer.sheets['Suscriptores']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Máximo 50 caracteres
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Preparar la respuesta HTTP
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="suscriptores_malvinas3d.xlsx"'
        
        return response
    
    exportar_excel.short_description = "Exportar suscriptores seleccionados a Excel"
    
    
    # Fieldsets para organizar la información
    fieldsets = [
        ('Información Personal', {'fields': ['nombre', 'apellido', 'nombre_institucion', 'email', 'tipo']}),
        ('Contacto', {'fields': ['telefono', 'contactado']}),
        ('Dirección', {'fields': ['calle', 'numero', 'piso_depto', 'codigo_postal', 'ciudad', 'provincia']}),
        ('Otros Datos', {'fields': ['fecha_nacimiento', 'dni', 'como_se_entero', 'motivo_participacion']}),
        ('Estado', {'fields': ['foto_validada', 'diploma_entregado']}),
    ]

    def changelist_view(self, request, extra_context=None):
        """
        Personalizar la vista de lista para agregar botón de exportar todo
        """
        extra_context = extra_context or {}
        extra_context['has_export_button'] = True
        return super().changelist_view(request, extra_context)
    
    def get_urls(self):
        """
        Agregar URL personalizada para exportar todos los suscriptores
        """
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('exportar-todos/', self.admin_site.admin_view(self.exportar_todos_view), name='m3d_app_suscriptor_exportar_todos'),
        ]
        return custom_urls + urls
    
    def exportar_todos_view(self, request):
        """
        Vista para exportar todos los suscriptores
        """
        todos_los_suscriptores = self.get_queryset(request)
        return self.exportar_excel(request, todos_los_suscriptores)

# Configuración para Nodos de Recepción
class NodoRecepcionAdmin(admin.ModelAdmin):
    list_display = ('id', 'suscriptor', 'responsable_impresion', 'provincia', 'nodo_seleccionado')
    list_filter = ('provincia', 'nodo_seleccionado')
    search_fields = ('suscriptor__nombre', 'suscriptor__email', 'responsable_impresion')
    list_per_page = 20

# Configuración para Impresoras
class ImpresoraAdmin(admin.ModelAdmin):
    list_display = ('id', 'marcas_modelos_equipos', 'cantidad_equipos', 'anios_experiencia')
    search_fields = ('marcas_modelos_equipos',)
    list_per_page = 20

# Registrar modelos con sus clases Admin personalizadas
admin.site.register(Suscriptor, SuscriptorAdmin)
admin.site.register(InstitucionConImpresora)
admin.site.register(InstitucionSinImpresora)
admin.site.register(ParticularConImpresora)
admin.site.register(ParticularSinImpresora)
admin.site.register(NodoRecepcion, NodoRecepcionAdmin)
admin.site.register(Impresora, ImpresoraAdmin)
admin.site.register(Bloque, BloqueAdmin)