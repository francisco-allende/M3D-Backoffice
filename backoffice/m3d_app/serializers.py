from rest_framework import serializers
from .models.suscriptor.suscriptor import Suscriptor
from .models.suscriptor.particular_con_impresora import ParticularConImpresora
from .models.suscriptor.particular_sin_impresora import ParticularSinImpresora
from .models.suscriptor.institucion_con_impresora import InstitucionConImpresora
from .models.suscriptor.institucion_sin_impresora import InstitucionSinImpresora
from .models.impresora.impresora import Impresora
from .models.bloque3d.bloque import Bloque
from .models.nodos.nodo_recepcion import NodoRecepcion

class ImpresoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Impresora
        fields = '__all__'

class SuscriptorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suscriptor
        fields = '__all__'

class ParticularConImpresoraSerializer(serializers.ModelSerializer):
    suscriptor = SuscriptorSerializer(read_only=True)
    impresora = ImpresoraSerializer(read_only=True)
    
    class Meta:
        model = ParticularConImpresora
        fields = '__all__'

class ParticularSinImpresoraSerializer(serializers.ModelSerializer):
    suscriptor = SuscriptorSerializer(read_only=True)
    
    class Meta:
        model = ParticularSinImpresora
        fields = '__all__'

class InstitucionConImpresoraSerializer(serializers.ModelSerializer):
    suscriptor = SuscriptorSerializer(read_only=True)
    impresora = ImpresoraSerializer(read_only=True)
    
    class Meta:
        model = InstitucionConImpresora
        fields = '__all__'

class InstitucionSinImpresoraSerializer(serializers.ModelSerializer):
    suscriptor = SuscriptorSerializer(read_only=True)
    
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