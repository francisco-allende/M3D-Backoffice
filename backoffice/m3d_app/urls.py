"""
URL configuration for backoffice project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from backoffice.m3d_app.views import SuscriptorConBloquesViewSet
from m3d_app.views import my_view
from m3d_app.views import SuscriptorViewSet, ImpresoraViewSet, ParticularConImpresoraViewSet
from m3d_app.views import ParticularSinImpresoraViewSet, InstitucionConImpresoraViewSet, InstitucionSinImpresoraViewSet
from m3d_app.views import BloqueViewSet, NodoRecepcionViewSet

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
router.register(r'suscriptores-con-bloques', SuscriptorConBloquesViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Incluir las URLs de la API
    path('api/', include(router.urls)),
    # Incluir URLs de autenticación para el navegador API
    path('api-auth/', include('rest_framework.urls')),
]