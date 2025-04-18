from django.db import models
from ..suscriptor.suscriptor import Suscriptor
from ..choices.provincia import Provincia

class NodoRecepcion(models.Model):
    suscriptor = models.ForeignKey(Suscriptor, on_delete=models.CASCADE, related_name='nodos_recepcion')
    numero_orden = models.IntegerField()
    numero_bloque = models.CharField(max_length=20)
    responsable_impresion = models.CharField(max_length=200)
    calle = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    codigo_postal = models.CharField(max_length=10)
    localidad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, choices=Provincia.get_all_provincias)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    nodo_seleccionado = models.CharField(max_length=100, choices=Provincia.get_some_provincias)
    detalles_nodo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Nodo: {self.nodo_seleccionado} - {self.suscriptor}"

