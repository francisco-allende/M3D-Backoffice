# m3d_app/views.py
from rest_framework import viewsets
from django.shortcuts import render
from django.db.models import Q

from .models.suscriptor.suscriptor import Suscriptor
from .models.suscriptor.particular_con_impresora import ParticularConImpresora
from .models.suscriptor.particular_sin_impresora import ParticularSinImpresora
from .models.suscriptor.institucion_con_impresora import InstitucionConImpresora
from .models.suscriptor.institucion_sin_impresora import InstitucionSinImpresora
from .models.impresora.impresora import Impresora
from .models.bloque3d.bloque import Bloque
from .models.nodos.nodo_recepcion import NodoRecepcion

# Importaciones de serializadores desde tu archivo serializers.py
from .serializers import (
    SuscriptorConBloquesSerializer, SuscriptorSerializer, ImpresoraSerializer, 
    ParticularConImpresoraSerializer, ParticularSinImpresoraSerializer,
    InstitucionConImpresoraSerializer, InstitucionSinImpresoraSerializer,
    BloqueSerializer, NodoRecepcionSerializer
)

# Tu vista existente
def my_view(request):
    return render(request, 'template.html')

# ViewSets
class SuscriptorViewSet(viewsets.ModelViewSet):
    queryset = Suscriptor.objects.all()
    serializer_class = SuscriptorSerializer

class ImpresoraViewSet(viewsets.ModelViewSet):
    queryset = Impresora.objects.all()
    serializer_class = ImpresoraSerializer

class ParticularConImpresoraViewSet(viewsets.ModelViewSet):
    queryset = ParticularConImpresora.objects.all()
    serializer_class = ParticularConImpresoraSerializer

class ParticularSinImpresoraViewSet(viewsets.ModelViewSet):
    queryset = ParticularSinImpresora.objects.all()
    serializer_class = ParticularSinImpresoraSerializer

class InstitucionConImpresoraViewSet(viewsets.ModelViewSet):
    queryset = InstitucionConImpresora.objects.all()
    serializer_class = InstitucionConImpresoraSerializer

class InstitucionSinImpresoraViewSet(viewsets.ModelViewSet):
    queryset = InstitucionSinImpresora.objects.all()
    serializer_class = InstitucionSinImpresoraSerializer

class BloqueViewSet(viewsets.ModelViewSet):
    queryset = Bloque.objects.all()
    serializer_class = BloqueSerializer

class NodoRecepcionViewSet(viewsets.ModelViewSet):
    queryset = NodoRecepcion.objects.all()
    serializer_class = NodoRecepcionSerializer

# En m3d_app/views.py, añadir esta vista

class SuscriptorConBloquesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar suscriptores con sus bloques asignados.
    Permite filtrar por tipo de suscriptor, email y otros campos.
    """
    queryset = Suscriptor.objects.all().prefetch_related('bloques')
    serializer_class = SuscriptorConBloquesSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por tipo de suscriptor (particular, institucion)
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
            
        # Filtrar por email
        email = self.request.query_params.get('email', None)
        if email:
            queryset = queryset.filter(email__icontains=email)
            
        # Filtrar por nombre/apellido/nombre_institucion
        nombre = self.request.query_params.get('nombre', None)
        if nombre:
            queryset = queryset.filter(
                Q(nombre__icontains=nombre) | 
                Q(apellido__icontains=nombre) |
                Q(nombre_institucion__icontains=nombre)
            )
            
        # Solo incluir suscriptores que tienen bloques asignados
        solo_con_bloques = self.request.query_params.get('solo_con_bloques', 'true')
        if solo_con_bloques.lower() == 'true':
            queryset = queryset.filter(bloques__isnull=False).distinct()
            
        return queryset