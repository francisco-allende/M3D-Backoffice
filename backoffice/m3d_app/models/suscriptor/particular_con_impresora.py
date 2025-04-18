from django.db import models
from .suscriptor import Suscriptor
from ..impresora.impresora import Impresora

class ParticularConImpresora(models.Model):
    suscriptor = models.OneToOneField(Suscriptor, on_delete=models.CASCADE, related_name='particular_con_impresora')
    impresora = models.OneToOneField(Impresora, on_delete=models.CASCADE, related_name='particular', null=True, blank=True)

    def __str__(self):
        return f"{self.suscriptor.nombre} {self.suscriptor.apellido} (Con impresora)"