from django.db import models
from ..suscriptor.suscriptor import Suscriptor
from ..nodos.nodo_recepcion import NodoRecepcion
from ..choices.estado import Estado

class Bloque(models.Model):

    # Formato "05-01" -> Sección 5, bloque 1
    numero_bloque = models.CharField(max_length=20, unique=True)
    # Agregar esta línea después de numero_bloque
    nro_sorteo = models.CharField(max_length=50, blank=True, null=True, help_text='Número de sorteo asignado cuando el bloque tiene un suscriptor')
    
    # Campo derivado de numero_bloque (ej: "05" para "05-01")
    seccion = models.CharField(max_length=10, db_index=True)
    
    # Campo derivado de numero_bloque (ej: "01" para "05-01")
    numero = models.CharField(max_length=10, db_index=True)

    class Meta:
        verbose_name = "Admin Bloques"
        verbose_name_plural = "Admin Bloques"
    
    suscriptor = models.ForeignKey(
        Suscriptor, 
        on_delete=models.CASCADE, 
        related_name='bloques',
        null=True,
        blank=True
    )
    
    nodo_recepcion = models.ForeignKey(
        NodoRecepcion, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='bloques'
    )
    
    estado = models.CharField(
        max_length=20,
        choices=Estado.get_all_estados,
        default='libre'
    )
    
    fecha_asignacion = models.DateTimeField(null=True, blank=True)
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    fecha_entrega_nodo = models.DateTimeField(null=True, blank=True)
    fecha_recepcion_m3d = models.DateTimeField(null=True, blank=True)
    fecha_entrega_diploma = models.DateTimeField(null=True, blank=True)
    
    historia_asociada = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Bloque {self.numero_bloque}" + (f" - {self.suscriptor}" if self.suscriptor else " - Sin asignar")
    
    def save(self, *args, **kwargs):
        # Extraer sección y número al guardar
        if self.numero_bloque and '-' in self.numero_bloque:
            partes = self.numero_bloque.split('-')
            if len(partes) == 2:
                self.seccion = partes[0].strip()
                self.numero = partes[1].strip()
        
        # Si el estado cambia a 'asignado' y no hay fecha de asignación, establecerla
        if self.estado == 'asignado' and not self.fecha_asignacion and self.suscriptor:
            from django.utils import timezone
            self.fecha_asignacion = timezone.now()
            
        super().save(*args, **kwargs)