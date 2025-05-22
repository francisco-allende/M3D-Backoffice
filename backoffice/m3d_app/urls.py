from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from rest_framework import routers
from m3d_app.views import (
    my_view,
    SuscriptorViewSet,
    ImpresoraViewSet,
    ParticularConImpresoraViewSet,
    ParticularSinImpresoraViewSet,
    InstitucionConImpresoraViewSet,
    InstitucionSinImpresoraViewSet,
    BloqueViewSet,
    NodoRecepcionViewSet,
    SuscriptorConBloquesViewSet,
)

# Configurar el router para APIs
router = routers.DefaultRouter()
router.register(r'suscriptores', SuscriptorViewSet)
router.register(r'impresoras', ImpresoraViewSet)
router.register(r'particulares-con-impresora', ParticularConImpresoraViewSet)
router.register(r'particulares-sin-impresora', ParticularSinImpresoraViewSet)
router.register(r'instituciones-con-impresora', InstitucionConImpresoraViewSet)
router.register(r'instituciones-sin-impresora', InstitucionSinImpresoraViewSet)
router.register(r'bloques', BloqueViewSet)
router.register(r'nodos-recepcion', NodoRecepcionViewSet)
router.register(r'suscriptores-con-bloques', SuscriptorConBloquesViewSet, basename='suscriptor-con-bloques')


urlpatterns = [
    path('', lambda request: redirect('/admin/', permanent=True)), 
    path('admin/', admin.site.urls),
    # Incluir las URLs de la API
    path('api/', include(router.urls)),
    # Incluir URLs de autenticación para el navegador API
    path('api-auth/', include('rest_framework.urls')),
    # Tu URL existente
    path('my_view/', my_view),
]