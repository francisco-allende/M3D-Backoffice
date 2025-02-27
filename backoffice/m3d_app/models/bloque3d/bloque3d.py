from django.db import models
from ..suscriptor.suscriptor import Suscriptor
from ..nodos.nodo_recepcion import NodoRecepcion

class Bloque3D(models.Model):
    numero_bloque = models.CharField(max_length=20, unique=True)  # Ej: "05-01"
    suscriptor = models.ForeignKey(Suscriptor, on_delete=models.CASCADE, related_name='bloques')
    nodo_recepcion = models.ForeignKey(NodoRecepcion, on_delete=models.SET_NULL, null=True, blank=True, related_name='bloques')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)  # Fecha en que se le asignó el bloque al suscriptor
    recibido = models.BooleanField(default=False)  # Si el suscriptor ya lo recibió
    historia_asociada = models.TextField(blank=True, null=True)  # Breve historia del bloque

    def __str__(self):
        return f"Bloque {self.numero_bloque} - {self.suscriptor}"
