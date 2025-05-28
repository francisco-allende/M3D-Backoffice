# backoffice/mapa_malvinas/views.py - Versión corregida

from django.shortcuts import render
from .models.mapa_bloque.mapa_bloque import MapaBloque
from m3d_app.models.bloque3d.bloque import Bloque

def mapa_bloques(request):
    # Obtener todos los bloques del mapa
    mapa_bloques = MapaBloque.objects.all()
    
    # Obtener todos los bloques con su estado
    bloques_estado = {b.numero_bloque: b.estado for b in Bloque.objects.all()}
    
    # Crear un diccionario para acceso rápido a los bloques del mapa
    mapa_bloques_dict = {}
    for bloque in mapa_bloques:
        if bloque.seccion not in mapa_bloques_dict:
            mapa_bloques_dict[bloque.seccion] = {}
        mapa_bloques_dict[bloque.seccion][bloque.numero] = bloque
    
    # Generar TODAS las secciones del 01 al 60
    secciones = {}
    for seccion_num in range(1, 61):  # Del 1 al 60
        seccion_str = f"{seccion_num:02d}"  # "01", "02", etc.
        
        # Inicializar la estructura para esta sección
        secciones[seccion_str] = {1: [], 2: [], 3: [], 4: [], 5: []}
        
        # Llenar con bloques (si existen) o vacíos
        for numero in range(1, 26):  # Del 1 al 25 (5 filas de 5 bloques cada una)
            fila = (numero - 1) % 5 + 1
            numero_str = f"{numero:02d}"  # "01", "02", etc.
            numero_bloque = f"{seccion_str}-{numero_str}"
            
            # Verificar si existe el bloque en el mapa
            if (seccion_str in mapa_bloques_dict and 
                numero_str in mapa_bloques_dict[seccion_str]):
                
                bloque_mapa = mapa_bloques_dict[seccion_str][numero_str]
                estado = bloques_estado.get(bloque_mapa.numero_bloque, 'libre')
                
                bloque_info = {
                    'codigo': bloque_mapa.codigo,
                    'numero_bloque': bloque_mapa.numero_bloque,
                    'numero': bloque_mapa.numero,
                    'descripcion': bloque_mapa.descripcion,
                    'tipo': bloque_mapa.tipo,
                    'estado': estado
                }
            else:
                # Crear un bloque vacío si no existe
                bloque_info = {
                    'codigo': f"M3D {seccion_str}-{numero_str}",
                    'numero_bloque': numero_bloque,
                    'numero': numero_str,
                    'descripcion': 'Sin contenido',
                    'tipo': None,
                    'estado': 'libre'
                }
            
            secciones[seccion_str][fila].append(bloque_info)
    
    # Organizar las secciones en 6 filas de 10 secciones cada una
    filas = []
    
    for fila_num in range(6):  # 6 filas
        fila_secciones = []
        for col_num in range(10):  # 10 columnas
            seccion_num = fila_num * 10 + col_num + 1  # 1-60
            seccion_str = f"{seccion_num:02d}"  # "01"-"60"
            
            fila_secciones.append({
                'seccion': seccion_str,
                'filas_bloques': secciones[seccion_str]
            })
        
        filas.append(fila_secciones)
    
    return render(request, 'mapa_malvinas/mapa_bloques.html', {
        'filas': filas,
        'total_bloques': len(mapa_bloques)
    })