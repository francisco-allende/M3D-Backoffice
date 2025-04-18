# mapa_malvinas/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models.mapa_bloque.mapa_bloque import MapaBloque
from .models.choices.tipo_bloque import TipoBloque
from django import forms
from django.contrib.admin.actions import delete_selected

class MapaBloqueForm(forms.ModelForm):
    class Meta:
        model = MapaBloque
        fields = '__all__'
        widgets = {
            'tipo': forms.Select(choices=TipoBloque.get_all_tipos()),
        }

class MapaBloqueAdmin(admin.ModelAdmin):
    form = MapaBloqueForm
    list_display = ('codigo', 'seccion', 'numero', 'tipo', 'descripcion_completa')
    list_filter = ('seccion', 'tipo')
    search_fields = ('codigo', 'seccion', 'numero', 'descripcion')
    list_per_page = 25
    list_editable = ('tipo',)
    
    # Acciones personalizadas para guardar
    actions = ['guardar_cambios']
    
    # Fieldsets para organizar la información en la vista de detalle
    fieldsets = [
        ('Identificación', {'fields': ['codigo', 'seccion', 'numero', 'numero_bloque']}),
        ('Contenido', {'fields': ['descripcion', 'tipo']}),
        ('Ubicación', {'fields': ['coordenadas'], 'classes': ['collapse']}),
    ]
    
    def descripcion_completa(self, obj):
        # Mostrar la descripción completa, con saltos de línea formateados como HTML
        descripcion_html = obj.descripcion.replace('\n', '<br>')
        return format_html(descripcion_html)
    
    descripcion_completa.short_description = 'Descripción'
    
    def guardar_cambios(self, request, queryset):
        """
        Acción personalizada para guardar cambios en múltiples bloques.
        """
        cambios = 0
        for bloque in queryset:
            try:
                bloque.save()
                cambios += 1
            except Exception as e:
                self.message_user(request, f"Error al guardar bloque {bloque.codigo}: {str(e)}", messages.ERROR)
        
        self.message_user(request, f"{cambios} bloques guardados exitosamente.", messages.SUCCESS)
    
    guardar_cambios.short_description = "Guardar cambios seleccionados"

admin.site.register(MapaBloque, MapaBloqueAdmin)