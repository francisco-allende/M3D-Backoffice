from django.db import models

class Suscriptor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True, null=True)  # Para particulares
    nombre_institucion = models.CharField(max_length=200, blank=True, null=True)  # Para instituciones
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    calle = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    piso_depto = models.CharField(max_length=50, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10)
    ciudad = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(blank=True, null=True)  # Para particulares
    dni = models.CharField(max_length=20, blank=True, null=True)  # Para particulares
    fecha_registro = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=20, choices=[('particular', 'Particular'), ('institucion', 'Institución')])
    como_se_entero = models.TextField(blank=True, null=True)
    motivo_participacion = models.TextField(blank=True, null=True)
    foto_validada = models.BooleanField(default=False)
    diploma_entregado = models.BooleanField(default=False)
    contactado = models.BooleanField(default=False)

    def __str__(self):
        if self.nombre_institucion:
            return f"{self.nombre_institucion} - {self.email}"
        apellido = self.apellido or ""  # Si apellido es None, usa una cadena vacía
        return f"{self.nombre} {apellido} —  {self.email}".strip()  # strip() elimina espacios en blanco sobrantes