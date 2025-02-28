# m3d_app/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models.suscriptor.suscriptor import Suscriptor
from .models.suscriptor.particular_con_impresora import ParticularConImpresora
from .models.suscriptor.particular_sin_impresora import ParticularSinImpresora
from .models.suscriptor.institucion_con_impresora import InstitucionConImpresora
from .models.suscriptor.institucion_sin_impresora import InstitucionSinImpresora
from .models.impresora.impresora import Impresora
from .models.bloque3d.bloque import Bloque
from .models.nodos.nodo_recepcion import NodoRecepcion
from django.shortcuts import render

# Tu vista existente
def my_view(request):
    return render(request, 'template.html')

# Primero, necesitas crear los serializadores
from rest_framework import serializers

class SuscriptorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suscriptor
        fields = '__all__'

class ImpresoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Impresora
        fields = '__all__'

class ParticularConImpresoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticularConImpresora
        fields = '__all__'

class ParticularSinImpresoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticularSinImpresora
        fields = '__all__'

class InstitucionConImpresoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitucionConImpresora
        fields = '__all__'

class InstitucionSinImpresoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitucionSinImpresora
        fields = '__all__'

class BloqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bloque
        fields = '__all__'

class NodoRecepcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodoRecepcion
        fields = '__all__'

# Luego, los ViewSets
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