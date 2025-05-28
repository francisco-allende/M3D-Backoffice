# backoffice/mapa_malvinas/views.py

from django.shortcuts import render
from .models.mapa_bloque.mapa_bloque import MapaBloque
from m3d_app.models.bloque3d.bloque import Bloque

def mapa_bloques(request):
    # Obtener todos los bloques del mapa
    mapa_bloques = MapaBloque.objects.all().order_by('seccion', 'numero')
    
    # Obtener todos los bloques con su estado
    bloques_estado = {b.numero_bloque: b.estado for b in Bloque.objects.all()}
    
    # Organizar bloques por sección y fila
    secciones = {}
    for bloque in mapa_bloques:
        seccion = bloque.seccion
        numero = int(bloque.numero)
        
        # Determinar la fila dentro de la sección (1-5)
        fila = (numero - 1) % 5 + 1
        
        # Inicializar la estructura si es necesario
        if seccion not in secciones:
            secciones[seccion] = {1: [], 2: [], 3: [], 4: [], 5: []}
        
        # Determinar estado (si no existe en bloques_estado, se considera 'libre')
        estado = bloques_estado.get(bloque.numero_bloque, 'libre')
        
        # Agregar bloque a la fila correspondiente
        secciones[seccion][fila].append({
            'codigo': bloque.codigo,
            'numero_bloque': bloque.numero_bloque,
            'numero': bloque.numero,
            'descripcion': bloque.descripcion,
            'tipo': bloque.tipo,
            'estado': estado
        })
    
    # Organizar las secciones en filas (10 secciones por fila para 6 filas total)
    filas = []
    secciones_ordenadas = sorted(secciones.keys())
    
    # Cambiar de 5 a 10 secciones por fila
    for i in range(0, len(secciones_ordenadas), 10):
        fila_secciones = []
        for seccion in secciones_ordenadas[i:i+10]:
            fila_secciones.append({
                'seccion': seccion,
                'filas_bloques': secciones[seccion]
            })
        filas.append(fila_secciones)
    
    return render(request, 'mapa_malvinas/mapa_bloques.html', {
        'filas': filas,
        'total_bloques': len(mapa_bloques)
    })