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

admin.site.register(Suscriptor)
admin.site.register(InstitucionConImpresora)
admin.site.register(InstitucionSinImpresora)
admin.site.register(ParticularConImpresora)
admin.site.register(ParticularSinImpresora)
admin.site.register(NodoRecepcion)
admin.site.register(Impresora)
admin.site.register(Bloque, BloqueAdmin)