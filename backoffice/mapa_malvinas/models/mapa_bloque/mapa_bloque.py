from django.db import models
from ..choices.tipo_bloque import TipoBloque

class MapaBloque(models.Model):
    codigo = models.CharField(max_length=50, unique=True)  # Ej: "M3D 01-01"
    descripcion = models.TextField()  # Breve descripción del bloque del mapa
    coordenadas = models.CharField(max_length=100, blank=True, null=True)  # Latitud y longitud opcional
    tipo = models.CharField(
        max_length=50,
        choices=TipoBloque.get_all_tipos,
        blank=True,
        null=True,
    )
    #poster = models.ForeignKey('PosterSeccion', on_delete=models.SET_NULL, null=True, blank=True, related_name='bloques')

    def __str__(self):
        return f"{self.codigo} - {self.tipo}"
