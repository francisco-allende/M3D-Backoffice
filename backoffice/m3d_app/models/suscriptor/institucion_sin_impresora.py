from django.db import models
from .suscriptor import Suscriptor

class InstitucionSinImpresora(models.Model):
    suscriptor = models.OneToOneField(Suscriptor, on_delete=models.CASCADE, related_name='institucion_sin_impresora')
    nombre_responsable = models.CharField(max_length=100, blank=True, null=True)
    dni_responsable = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.suscriptor.nombre_institucion} (Sin impresora)"