# mapa_malvinas/models/mapa_bloque/mapa_bloque.py

from django.db import models
from ..choices.tipo_bloque import TipoBloque

class MapaBloque(models.Model):
    # Código en formato "M3D 05-01" (corresponde a la sección 5, bloque 1)
    codigo = models.CharField(max_length=50, unique=True)
    
    # Campos derivados para facilitar búsquedas
    seccion = models.CharField(max_length=10, db_index=True)
    numero = models.CharField(max_length=10, db_index=True)
    
    # Formato estándar para relacionar con m3d_app.Bloque (ej: "05-01")
    numero_bloque = models.CharField(max_length=20, db_index=True)
    
    descripcion = models.TextField()  # Breve descripción del bloque del mapa
    coordenadas = models.CharField(max_length=100, blank=True, null=True)  # Latitud y longitud opcional
    
    tipo = models.CharField(
        max_length=50,
        choices=TipoBloque.get_all_tipos,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Historia Bloque"
        verbose_name_plural = "Historia Bloques"
    
    def __str__(self):
        return f"{self.codigo} - {self.tipo}"
    
    def save(self, *args, **kwargs):
        # Extraer número de bloque del código (quitar "M3D " del inicio)
        if self.codigo and self.codigo.startswith("M3D "):
            self.numero_bloque = self.codigo[4:].strip()
            
            # Extraer sección y número
            if '-' in self.numero_bloque:
                partes = self.numero_bloque.split('-')
                if len(partes) == 2:
                    self.seccion = partes[0].strip()
                    self.numero = partes[1].strip()
                    
        super().save(*args, **kwargs)