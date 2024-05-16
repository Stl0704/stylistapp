from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.hashers import make_password, check_password


class Genero(models.Model):
    genero_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=45)
    descripcion = models.CharField(max_length=45)

class Persona(models.Model):
    persona_id = models.AutoField(primary_key=True)
    fecha_nac = models.DateField()
    genero = models.ForeignKey(Genero, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=55)
    apellido1 = models.CharField(max_length=30)
    apellido2 = models.CharField(max_length=30)

class Usuario(models.Model):
    user_id = models.AutoField(primary_key=True, serialize=False)
    user_name = models.CharField(max_length=45, unique=True)
    email = models.EmailField(max_length=45)
    password = models.CharField(max_length=128)  # Aumenta el tamaño para almacenar el hash

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

class TipoUsuario(models.Model):
    tipo_user_id = models.AutoField(primary_key=True)
    nombre_tipo_user = models.CharField(max_length=45)
    descripcion = models.CharField(max_length=45)

class PersonaUsuario(models.Model):
    persona_user_id = models.AutoField(primary_key=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo_user = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE)

class Cliente(models.Model):
    cliente_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)

class PrestadorServicios(models.Model):
    prestador_serv_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    especialidad = models.CharField(max_length=350)
    experiencia = models.CharField(max_length=450)
    presentacion = models.CharField(max_length=200)
    calificacion = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

class Servicio(models.Model):
    servicio_id = models.AutoField(primary_key=True)
    
class HistorialCompra(models.Model):
    hist_id = models.AutoField(primary_key=True)
    calificacion = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

class Local(models.Model):
    local_id = models.AutoField(primary_key=True)
    nombre_local = models.CharField(max_length=45)
    direcciones = models.CharField(max_length=100)

class ServicioAPrestar(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    prestador_serv = models.ForeignKey(PrestadorServicios, on_delete=models.CASCADE)
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
    tarifa = models.DecimalField(max_digits=10, decimal_places=2)
    disponibilidad = models.CharField(max_length=150)

class Cita(models.Model):
    cita_id = models.AutoField(primary_key=True)
    prestador_serv = models.ForeignKey(PrestadorServicios, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    duracion = models.TimeField()
    local = models.ForeignKey(Local, on_delete=models.CASCADE)

class Distrito(models.Model):
    distrito_id = models.AutoField(primary_key=True)
    nombre_distrito = models.CharField(max_length=45)
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
