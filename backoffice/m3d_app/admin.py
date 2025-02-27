from django.contrib import admin
from .models.suscriptor.suscriptor import Suscriptor 
from .models.suscriptor.institucion_con_impresora import InstitucionConImpresora
from .models.suscriptor.institucion_sin_impresora import InstitucionSinImpresora
from .models.suscriptor.particular_con_impresora import ParticularConImpresora
from .models.suscriptor.particular_sin_impresora import ParticularSinImpresora
from .models.nodos.nodo_recepcion import NodoRecepcion
from .models.impresora.impresora import Impresora

admin.site.register(Suscriptor)
admin.site.register(InstitucionConImpresora)
admin.site.register(InstitucionSinImpresora)
admin.site.register(ParticularConImpresora)
admin.site.register(ParticularSinImpresora)
admin.site.register(NodoRecepcion)
admin.site.register(Impresora)

