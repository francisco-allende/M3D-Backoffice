# mapa_malvinas/urls.py
from django.urls import path
from . import views

app_name = 'mapa_malvinas'

urlpatterns = [
    path('mapa-bloques/', views.mapa_bloques, name='mapa_bloques'),
]