from django.db import models
from .suscriptor import Suscriptor

class ParticularSinImpresora(models.Model):
    suscriptor = models.OneToOneField(Suscriptor, on_delete=models.CASCADE, related_name='particular_sin_impresora')

    def __str__(self):
        return f"{self.suscriptor.nombre} {self.suscriptor.apellido} (Sin impresora)"