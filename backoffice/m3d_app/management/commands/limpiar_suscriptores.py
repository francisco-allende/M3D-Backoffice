# m3d_app/management/commands/limpiar_suscriptores.py

from django.core.management.base import BaseCommand
from m3d_app.models.suscriptor.suscriptor import Suscriptor
import re
from datetime import datetime
from django.db import transaction

class Command(BaseCommand):
    help = 'Limpia y reorganiza los datos de los suscriptores'

    def handle(self, *args, **options):
        suscriptores = Suscriptor.objects.all()
        
        actualizados = 0
        sin_cambios = 0
        errores = 0
        
        for suscriptor in suscriptores:
            try:
                with transaction.atomic():
                    # Guardar datos originales para comparar después
                    datos_originales = {
                        'nombre': suscriptor.nombre,
                        'apellido': suscriptor.apellido,
                        'telefono': suscriptor.telefono,
                        'calle': suscriptor.calle,
                        'numero': suscriptor.numero,
                        'piso_depto': suscriptor.piso_depto,
                        'ciudad': suscriptor.ciudad,
                        'fecha_nacimiento': suscriptor.fecha_nacimiento
                    }
                    
                    cambios = False
                    
                    # Procesar el nombre (puede contener más información)
                    if suscriptor.nombre:
                        # Extraer fecha de nacimiento
                        fecha_match = re.search(r'Fecha de nacimiento: (\d{4}-\d{2}-\d{2})', suscriptor.nombre)
                        if fecha_match and not suscriptor.fecha_nacimiento:
                            fecha_str = fecha_match.group(1)
                            try:
                                suscriptor.fecha_nacimiento = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                                cambios = True
                            except ValueError:
                                self.stdout.write(self.style.WARNING(f"Formato de fecha inválido: {fecha_str} para {suscriptor.email}"))
                        
                        # Extraer calle
                        calle_match = re.search(r'Calle: ([^,>]+)', suscriptor.nombre)
                        if calle_match and (not suscriptor.calle or suscriptor.calle == "Sin datos"):
                            suscriptor.calle = calle_match.group(1).strip()
                            cambios = True
                        
                        # Extraer número
                        nro_match = re.search(r'Nro: ([^,>]+)', suscriptor.nombre)
                        if nro_match and (not suscriptor.numero or suscriptor.numero == "S/N"):
                            suscriptor.numero = nro_match.group(1).strip()
                            cambios = True
                            
                        # Extraer piso y depto
                        piso_match = re.search(r'Piso (?:y Depto:? )?([^,>]+)', suscriptor.nombre)
                        if piso_match and not suscriptor.piso_depto:
                            suscriptor.piso_depto = piso_match.group(1).strip()
                            cambios = True
                            
                        # Extraer ciudad
                        ciudad_match = re.search(r'Ciudad (?:de )?([^,>]+)', suscriptor.nombre)
                        if ciudad_match and (not suscriptor.ciudad or suscriptor.ciudad == "Sin datos"):
                            suscriptor.ciudad = ciudad_match.group(1).strip()
                            cambios = True
                        
                        # Extraer teléfono (formato +54...)
                        tel_match = re.search(r'\+(\d+)', suscriptor.nombre)
                        if tel_match and (not suscriptor.telefono or suscriptor.telefono == "0000000000"):
                            suscriptor.telefono = "+" + tel_match.group(1).strip()
                            cambios = True
                            
                        # Limpiar el nombre
                        nombre_limpio = suscriptor.nombre
                        
                        # Quitar toda la información extraída para limpiar el nombre
                        patrones = [
                            r'Fecha de nacimiento: \d{4}-\d{2}-\d{2}',
                            r'Calle: [^,>]+',
                            r'Nro: [^,>]+',
                            r'Piso (?:y Depto:? )?[^,>]+',
                            r'Ciudad (?:de )?[^,>]+',
                            r'\+\d+'
                        ]
                        
                        for patron in patrones:
                            nombre_limpio = re.sub(patron, '', nombre_limpio)
                        
                        # Limpiar múltiples comas, ">", etc.
                        nombre_limpio = re.sub(r'[,>]+', ',', nombre_limpio)
                        nombre_limpio = re.sub(r',\s*,', ',', nombre_limpio)
                        nombre_limpio = re.sub(r'^[,\s]+|[,\s]+$', '', nombre_limpio)
                        
                        # Si hay una coma, separar en nombre y apellido
                        if ',' in nombre_limpio and not suscriptor.apellido:
                            partes = nombre_limpio.split(',', 1)
                            if len(partes) == 2:
                                suscriptor.nombre = partes[0].strip()
                                suscriptor.apellido = partes[1].strip()
                                cambios = True
                            else:
                                suscriptor.nombre = nombre_limpio.strip()
                        else:
                            suscriptor.nombre = nombre_limpio.strip()
                            
                        if suscriptor.nombre != datos_originales['nombre']:
                            cambios = True
                    
                    # Si hubo cambios, guardar
                    if cambios:
                        suscriptor.save()
                        actualizados += 1
                        self.stdout.write(f"Actualizado: {suscriptor.email} - {suscriptor.nombre} {suscriptor.apellido or ''}")
                    else:
                        sin_cambios += 1
                        
            except Exception as e:
                errores += 1
                self.stdout.write(self.style.ERROR(f"Error al procesar {suscriptor.email}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(
            f"Proceso completado: {actualizados} suscriptores actualizados, "
            f"{sin_cambios} sin cambios, {errores} errores"
        ))