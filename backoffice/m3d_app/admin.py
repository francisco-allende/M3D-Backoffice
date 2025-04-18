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

# Clase para mejorar la visualización de Bloques en el admin
class BloqueAdmin(admin.ModelAdmin):
    list_display = ('numero_bloque', 'seccion', 'numero', 'suscriptor', 'estado', 'fecha_asignacion')
    list_filter = ('seccion', 'estado')
    search_fields = ('numero_bloque', 'seccion', 'numero', 'suscriptor__nombre', 'suscriptor__nombre_institucion')
    readonly_fields = ('seccion', 'numero')
    date_hierarchy = 'fecha_asignacion'
    list_per_page = 20
    
    # Para mejorar la apariencia en Jazzmin
    list_display_links = ('numero_bloque',)
    
    # Fieldsets para organizar la información en pestañas
    fieldsets = [
        ('Información del Bloque', {'fields': ['numero_bloque', 'seccion', 'numero', 'suscriptor', 'estado']}),
        ('Fechas', {'fields': ['fecha_asignacion', 'fecha_validacion', 'fecha_entrega_nodo', 'fecha_recepcion_m3d', 'fecha_entrega_diploma']}),
        ('Otros Datos', {'fields': ['nodo_recepcion', 'historia_asociada']}),
    ]

# Clase para la visualización de Suscriptor con sus bloques
class SuscriptorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'nombre_institucion', 'email', 'tipo', 'telefono', 'provincia', 'get_bloques_count')
    list_filter = ('tipo', 'provincia', 'contactado')
    search_fields = ('nombre', 'apellido', 'nombre_institucion', 'email', 'telefono')
    list_per_page = 20
    
    def get_bloques_count(self, obj):
        return obj.bloques.count()
    get_bloques_count.short_description = 'Bloques'
    
    # Fieldsets para organizar la información
    fieldsets = [
        ('Información Personal', {'fields': ['nombre', 'apellido', 'nombre_institucion', 'email', 'tipo']}),
        ('Contacto', {'fields': ['telefono', 'contactado']}),
        ('Dirección', {'fields': ['calle', 'numero', 'piso_depto', 'codigo_postal', 'ciudad', 'provincia']}),
        ('Otros Datos', {'fields': ['fecha_nacimiento', 'dni', 'como_se_entero', 'motivo_participacion']}),
        ('Estado', {'fields': ['foto_validada', 'diploma_entregado']}),
    ]

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