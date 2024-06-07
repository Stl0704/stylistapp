from django.db import models
from polymorphic.models import PolymorphicModel
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


class Usuario(PolymorphicModel):
    user_id = models.AutoField(primary_key=True, serialize=False)
    user_name = models.CharField(max_length=45, unique=True)
    email = models.EmailField(max_length=45)
    password = models.CharField(max_length=128)
    tipo_usuario = models.CharField(max_length=50, choices=(
        ('cliente', 'Cliente'), ('prestador', 'Prestador')))

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class PersonaUsuario(models.Model):
    persona_user_id = models.AutoField(primary_key=True)
    persona = models.ForeignKey('Persona', on_delete=models.CASCADE)
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE)


class Cliente(Usuario):
    img = models.CharField(max_length=350)
    puntos = models.IntegerField(default=0)


class PrestadorServicios(Usuario):
    especialidad = models.CharField(max_length=350)
    experiencia = models.CharField(max_length=450)
    presentacion = models.CharField(max_length=200)
    calificacion = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )


class Servicio(models.Model):
    servicio_id = models.AutoField(primary_key=True)
    duracion_serv = models.TimeField()
    nombre_serv = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=100)
    foto = models.CharField(
        max_length=1000, default='Descripción no proporcionada')
    descripcion = models.TextField(
        max_length=200, default='Descripción no proporcionada')

    def __str__(self):
        return self.nombre_serv


class Local(models.Model):
    local_id = models.AutoField(primary_key=True)
    nombre_local = models.CharField(max_length=45)
    direcciones = models.CharField(max_length=100)


class Producto(models.Model):
    prod_id = models.AutoField(primary_key=True)
    nombre_prod = models.CharField(max_length=100)
    foto = models.CharField(max_length=1000, default='Imagen no proporcionada')
    cantidad = models.PositiveIntegerField(default=0)  # Inventario inicial
    a_la_venta = models.BooleanField(default=False)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(
        max_length=200, default='Descripción no proporcionada')
    sku_id = models.CharField(max_length=50)
    local = models.ForeignKey(
        'Local', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre_prod


class ServicioAPrestar(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    prestador_serv = models.ForeignKey(
        PrestadorServicios, on_delete=models.CASCADE)
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
    tarifa = models.DecimalField(max_digits=10, decimal_places=2)
    disponibilidad = models.CharField(max_length=150)


class HistorialCompra(models.Model):
    hist_id = models.AutoField(primary_key=True)
    calificacion = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    boleta = models.ForeignKey('Boleta', on_delete=models.CASCADE)


class Cita(models.Model):
    cita_id = models.AutoField(primary_key=True)
    prestador_serv = models.ForeignKey(
        PrestadorServicios, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    duracion = models.TimeField()
    local = models.ForeignKey('Local', on_delete=models.CASCADE)
    boleta = models.OneToOneField(
        'Boleta', on_delete=models.CASCADE, null=True, blank=True, related_name='cita_cita')


class Boleta(models.Model):
    boleta_id = models.AutoField(primary_key=True)
    cita = models.ForeignKey(
        Cita, on_delete=models.CASCADE, related_name='boleta_boletas')
    fecha_emision = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=45)
    transaccion_id = models.CharField(max_length=45, unique=True)


class Distrito(models.Model):
    distrito_id = models.AutoField(primary_key=True)
    nombre_distrito = models.CharField(max_length=45)
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
