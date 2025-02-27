from django.db import models

class Impresora(models.Model):
    anios_experiencia = models.IntegerField(blank=True, null=True)
    marcas_modelos_equipos = models.TextField(blank=True, null=True)
    materiales_uso = models.TextField(blank=True, null=True)
    cantidad_equipos = models.IntegerField(blank=True, null=True)
    dimension_maxima_impresion = models.CharField(max_length=50, blank=True, null=True)
    software_uso = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.marcas_modelos_equipos} ({self.cantidad_equipos} equipos)"
