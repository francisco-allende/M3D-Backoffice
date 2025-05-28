# backoffice/mapa_malvinas/views.py - Versión corregida para manejar asterisco

from django.shortcuts import render
from .models.mapa_bloque.mapa_bloque import MapaBloque
from m3d_app.models.bloque3d.bloque import Bloque

def mapa_bloques(request):
    # Obtener todos los bloques del mapa (los 1500)
    mapa_bloques = MapaBloque.objects.all()
    
    # Obtener todos los bloques con estado (los ~900)
    # CREAR DOS ÍNDICES: uno con asterisco y otro sin asterisco
    bloques_estado = {}
    bloques_estado_con_asterisco = {}
    
    for b in Bloque.objects.all():
        bloques_estado[b.numero_bloque] = b.estado
        
        # Si el numero_bloque tiene asterisco, crear versión sin asterisco
        if b.numero_bloque.startswith('*'):
            numero_sin_asterisco = b.numero_bloque[1:]  # Quitar el asterisco
            bloques_estado_con_asterisco[numero_sin_asterisco] = b.estado
    
    print(f"DEBUG - Total bloques mapa: {len(mapa_bloques)}")
    print(f"DEBUG - Total bloques con estado (con *): {len(bloques_estado)}")
    print(f"DEBUG - Total bloques con estado (sin *): {len(bloques_estado_con_asterisco)}")
    print(f"DEBUG - Ejemplos sin asterisco: {list(bloques_estado_con_asterisco.items())[:5]}")
    
    # Crear un diccionario para acceso rápido a los bloques del mapa
    mapa_bloques_dict = {}
    for bloque in mapa_bloques:
        if bloque.seccion not in mapa_bloques_dict:
            mapa_bloques_dict[bloque.seccion] = {}
        mapa_bloques_dict[bloque.seccion][bloque.numero] = bloque
    
    # Generar TODAS las secciones del 01 al 60
    secciones = {}
    bloques_con_estado_encontrados = 0
    
    for seccion_num in range(1, 61):  # Del 1 al 60
        seccion_str = f"{seccion_num:02d}"  # "01", "02", etc.
        
        # Inicializar la estructura para esta sección
        secciones[seccion_str] = {1: [], 2: [], 3: [], 4: [], 5: []}
        
        # Llenar con bloques (si existen) o vacíos
        for numero in range(1, 26):  # Del 1 al 25 (5 filas de 5 bloques cada una)
            fila = (numero - 1) % 5 + 1
            numero_str = f"{numero:02d}"  # "01", "02", etc.
            numero_bloque_mapa = f"{seccion_str}-{numero_str}"  # Formato MapaBloque: "01-01"
            
            # Verificar si existe el bloque en el mapa
            if (seccion_str in mapa_bloques_dict and 
                numero_str in mapa_bloques_dict[seccion_str]):
                
                bloque_mapa = mapa_bloques_dict[seccion_str][numero_str]
                
                # BUSCAR ESTADO: primero sin asterisco, luego con asterisco
                estado_real = 'libre'  # Default
                
                # Opción 1: Buscar en bloques_estado_con_asterisco (sin asterisco)
                if numero_bloque_mapa in bloques_estado_con_asterisco:
                    estado_real = bloques_estado_con_asterisco[numero_bloque_mapa]
                    bloques_con_estado_encontrados += 1
                    if seccion_num <= 2:  # Debug para primeras secciones
                        print(f"DEBUG - Encontrado {numero_bloque_mapa} -> {estado_real}")
                
                # Opción 2: Buscar con asterisco por si acaso
                elif f"*{numero_bloque_mapa}" in bloques_estado:
                    estado_real = bloques_estado[f"*{numero_bloque_mapa}"]
                    bloques_con_estado_encontrados += 1
                
                bloque_info = {
                    'codigo': bloque_mapa.codigo,
                    'numero_bloque': bloque_mapa.numero_bloque,
                    'numero': bloque_mapa.numero,
                    'descripcion': bloque_mapa.descripcion,
                    'tipo': bloque_mapa.tipo,
                    'estado': estado_real
                }
            else:
                # Crear un bloque vacío si no existe en MapaBloque
                # Pero aún verificar si existe en Bloque
                estado_fallback = 'libre'
                if numero_bloque_mapa in bloques_estado_con_asterisco:
                    estado_fallback = bloques_estado_con_asterisco[numero_bloque_mapa]
                elif f"*{numero_bloque_mapa}" in bloques_estado:
                    estado_fallback = bloques_estado[f"*{numero_bloque_mapa}"]
                
                bloque_info = {
                    'codigo': f"M3D {seccion_str}-{numero_str}",
                    'numero_bloque': numero_bloque_mapa,
                    'numero': numero_str,
                    'descripcion': 'Sin contenido',
                    'tipo': None,
                    'estado': estado_fallback
                }
            
            secciones[seccion_str][fila].append(bloque_info)
    
    print(f"DEBUG - Bloques con estado encontrados en el mapa: {bloques_con_estado_encontrados}")
    
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
    
    # Debug final: contar estados
    conteo_estados = {}
    for seccion in secciones.values():
        for fila in seccion.values():
            for bloque in fila:
                estado = bloque['estado']
                conteo_estados[estado] = conteo_estados.get(estado, 0) + 1
    
    print(f"DEBUG - Conteo de estados en el mapa:")
    for estado, count in conteo_estados.items():
        print(f"  - {estado}: {count}")
    
    return render(request, 'mapa_malvinas/mapa_bloques.html', {
        'filas': filas,
        'total_bloques': len(mapa_bloques)
    })