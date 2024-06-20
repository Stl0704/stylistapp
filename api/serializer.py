from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import authenticate
from .models import *
from uuid import uuid4


# PERSONA


class PersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ['nombre', 'apellido1', 'apellido2', 'fecha_nac', 'genero']

    def create(self, validated_data):
        return Persona.objects.create(**validated_data)


# PRESTADOR DE SERVICIOS

class PrestadorServiciosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrestadorServicios
        fields = ['prestador_serv_id', 'user', 'especialidad',
                  'experiencia', 'presentacion', 'calificacion']


# SERVICIO A PRESTAR

class ServicioAPrestarSerializer(serializers.ModelSerializer):
    servicio = serializers.StringRelatedField()
    prestador_serv = PrestadorServiciosSerializer(read_only=True)
    local = serializers.StringRelatedField()

    class Meta:
        model = ServicioAPrestar
        fields = ['servicio', 'prestador_serv',
                  'local', 'tarifa', 'disponibilidad']


# ENDPOINT GENERAL


# python manage.py runserver 0.0.0.0:9000
# PETICIONES :


# USUARIOS:

# PETICION INICIO SESION

# {
#   "user_name": "mario",
#   "password": "12345678"
# }

# REGISTRO DE PRODUCTO

# {
#     "nombre_prod": "fijador",
#     "foto": "https://tuachl.vtexassets.com/arquivos/ids/157942-1200-auto?v=637459174431200000&width=1200&height=auto&aspect=true",
#     "cantidad": null,
#     "a_la_venta": true,
#     "precio": 99000,
#     "precio_venta": 99000,
#     "descripcion": "Contiene 9 extractos botánicos que contribuyen a recuperar la hidratación perdida y a conseguir un cabello con aspecto saludable y rejuvenecido.",
#     "sku_id": "CCCTR0081127178",
#     "local": null
# }


# SOLICITUD CREACION USUARIO CLIENTE:


# {
#     "user_name": "Mario",
#     "email": "mario@example.com",
#     "password": "12345678",
#     "tipo_usuario": "cliente",
#     "fecha_nac": "1985-09-16",
#     "genero_id": 1,
#     "nombrep": "Mario",
#     "apellido1_persona": "Bros",
#     "apellido2_persona": "Nintendo"
# }


# SOLICITUD CREACION USUARIO PRESTADOR DE SERVICIOS


# {
#     "user_name": "Dani",
#     "email": "usuario@example.com",
#     "password": "12345678",
#     "tipo_usuario": "prestador",
#     "fecha_nac": "1990-01-01",
#     "genero_id": 1,
#     "nombrep": "Daniel",
#     "apellido1_persona": "Paz",
#     "apellido2_persona": "nose",
#     "especialidad": "Cortes de cabello medievales",
#     "experiencia": "300 años",
#     "presentacion": "Experto en estilos antiguos y técnicas medievales de corte.",
#     "calificacion": 0.0
# }


# LOCALES:

# CREAR LOCAL

# {
#   "nombre": "Local de Prestador",
#   "direccion": "123 Calle Ficticia",
#   "prestador_id": "1",
#   "comuna":"31"
# }


# PRODUCTOS:

# PETICION CREAR PRODUCTO

# {
#     "nombre_prod": "Crema Hidratante",
#     "foto": "url-a-la-imagen-de-la-crema.jpg",
#     "cantidad": 100,
#     "a_la_venta": true,
#     "precio": 19990.00,
#     "descripcion": "Crema hidratante para todo tipo de piel, 100ml.",
#     "sku_id": "CREM100ML",
#     "local": 1
# }


# PETICION MODIFICAR PRODUCTO:

# {
#   "user_id": 2,
#   "cantidad": 50,
#   "descripcion": "Contiene 56 extractos botánicos que contribuyen a recuperar la hidratación perdida y a conseguir un cabello con aspecto saludable y rejuvenecido.",
#   "precio": 222222
# }


# ENDPOINT PARA ELIMINAR PRODUCTO:

#   http://172.20.10.5/api/v1/

# OJO: SOLO EL ID OWNER DEL LOCAL PODRA ELIMINAR EL PRODUCTO


# PETICION PARA AGENDAR CITA

# {
#     "tipo_usuario": "cliente",
#     "cliente_id": 2,
#     "prestador_serv_id": 3,
#     "local_id": 1,
#     "fecha_hora": "2024-06-30",
#     "duracion": "01:00:00",
#     "metodo_pago": "tarjeta",
#     "monto_total": 120.00
# }


# BOLETA Y HISTORIAL DE COMPRAS


# BOLETA


# {
#     "monto_total": "100.00",
#     "metodo_pago": "tarjeta",
#     "transaccion_id": "12345",
#     "cita": "1"
# }


#   SERIALIZADORES FUNCIONALES


# SERIALIZADOR CREACION USUARIO PRESTADOR DE SERVICIOS

class UsuarioPrestadorSerializer(serializers.ModelSerializer):
    fecha_nac = serializers.DateField()
    genero_id = serializers.IntegerField()  # Asume que se pasa un ID de género
    nombrep = serializers.CharField(max_length=55)
    apellido1_persona = serializers.CharField(max_length=30)
    apellido2_persona = serializers.CharField(max_length=30)
    especialidad = serializers.CharField(max_length=350)
    experiencia = serializers.CharField(max_length=450)
    presentacion = serializers.CharField(max_length=200)
    calificacion = serializers.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        model = PrestadorServicios
        fields = [
            'user_name', 'email', 'password', 'tipo_usuario', 'fecha_nac',
            'genero_id', 'nombrep', 'apellido1_persona', 'apellido2_persona',
            'especialidad', 'experiencia', 'presentacion', 'calificacion'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    @transaction.atomic
    def create(self, validated_data):
        # Creación de la entidad Persona
        genero = Genero.objects.get(pk=validated_data.pop('genero_id'))
        persona_data = {
            'nombre': validated_data.pop('nombrep'),
            'apellido1': validated_data.pop('apellido1_persona'),
            'apellido2': validated_data.pop('apellido2_persona'),
            'fecha_nac': validated_data.pop('fecha_nac'),
            'genero': genero,
        }
        persona = Persona.objects.create(**persona_data)

        # Extracción y creación de Usuario o PrestadorServicios
        password = validated_data.pop('password')
        usuario_data = {key: validated_data.pop(key) for key in [
            'user_name', 'email', 'tipo_usuario'] if key in validated_data}
        prestador_data = {key: validated_data.pop(key) for key in [
            'especialidad', 'experiencia', 'presentacion', 'calificacion'] if key in validated_data}

        usuario = PrestadorServicios(**usuario_data, **prestador_data)
        usuario.set_password(password)
        usuario.save()

        # Vinculación entre Persona y Usuario mediante PersonaUsuario
        PersonaUsuario.objects.create(persona=persona, user=usuario)

        return usuario


# SERIALIZADOR CREACION USUARIO CLIENTE

class UsuarioClienteSerializer(serializers.ModelSerializer):
    fecha_nac = serializers.DateField()
    genero_id = serializers.IntegerField()  # Asume que se pasa un ID de género
    nombrep = serializers.CharField(max_length=55)
    apellido1_persona = serializers.CharField(max_length=30)
    apellido2_persona = serializers.CharField(max_length=30)
    img = serializers.CharField(max_length=350, required=False)
    # Puntos comienzan en cero y no se actualizan en la creación
    puntos = serializers.IntegerField(default=0, read_only=True)

    class Meta:
        model = Cliente
        fields = [
            'user_name', 'email', 'password', 'tipo_usuario', 'fecha_nac',
            'genero_id', 'nombrep', 'apellido1_persona', 'apellido2_persona',
            'img', 'puntos'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    @transaction.atomic
    def create(self, validated_data):
        # Creación de la entidad Persona
        genero = Genero.objects.get(pk=validated_data.pop('genero_id'))
        persona_data = {
            'nombre': validated_data.pop('nombrep'),
            'apellido1': validated_data.pop('apellido1_persona'),
            'apellido2': validated_data.pop('apellido2_persona'),
            'fecha_nac': validated_data.pop('fecha_nac'),
            'genero': genero,
        }
        persona = Persona.objects.create(**persona_data)

        # Extracción y creación de Usuario o Cliente
        password = validated_data.pop('password')
        usuario_data = {key: validated_data.pop(key) for key in [
            'user_name', 'email', 'tipo_usuario'] if key in validated_data}
        cliente_data = {key: validated_data.pop(key, None) for key in [
            'img', 'puntos'] if key in validated_data}

        usuario = Cliente(**usuario_data, **cliente_data)
        usuario.set_password(password)
        usuario.save()

        # Vinculación entre Persona y Usuario mediante PersonaUsuario
        PersonaUsuario.objects.create(persona=persona, user=usuario)

        return usuario


# SERIALIZADOR  DE INICIO DE SESION:

class LoginSerializer(serializers.Serializer):
    user_name = serializers.CharField(max_length=45)
    password = serializers.CharField(max_length=45, write_only=True)

    def validate(self, data):
        user_name = data.get("user_name")
        password = data.get("password")
        user = authenticate(username=user_name, password=password)
        if user is None:
            raise serializers.ValidationError("Credenciales inválidas.")
        return data


# SERIALIZADOR TIPOS DE USUARIO :


class PrestadorServiciosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrestadorServicios
        fields = ['user_ptr_id', 'especialidad',
                  'experiencia', 'presentacion', 'calificacion']

    def create(self, validated_data):
        usuario_id = validated_data.pop('user_ptr_id')
        usuario = Usuario.objects.get(pk=usuario_id)
        prestador = PrestadorServicios.objects.create(
            user_ptr=usuario, **validated_data)
        return prestador


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['user_ptr_id', 'img', 'puntos']

    def create(self, validated_data):
        usuario_id = validated_data.pop('user_ptr_id')
        usuario = Usuario.objects.get(pk=usuario_id)
        cliente = Cliente.objects.create(user_ptr=usuario, **validated_data)
        return cliente


# SERIALIZADOR LOCAL-PRESTADOR:

class LocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Local
        fields = ['nombre', 'direccion', 'prestador', 'comuna']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        return Local.objects.create(**validated_data)


# SERIALIZADOR CITAS:

class CitaSerializer(serializers.ModelSerializer):
    cliente_id = serializers.IntegerField(write_only=True)
    prestador_serv_id = serializers.IntegerField(write_only=True)
    local_id = serializers.PrimaryKeyRelatedField(
        queryset=Local.objects.all(), write_only=True)
    metodo_pago = serializers.CharField(max_length=45, write_only=True)
    monto_total = serializers.DecimalField(
        max_digits=10, decimal_places=2, write_only=True)

    class Meta:
        model = Cita
        fields = ['fecha_hora', 'duracion', 'cliente_id',
                  'prestador_serv_id', 'local_id', 'metodo_pago', 'monto_total']

    @transaction.atomic
    def create(self, validated_data):
        cliente_id = validated_data.pop('cliente_id')
        prestador_serv_id = validated_data.pop('prestador_serv_id')
        local_id = validated_data.pop('local_id')

        cliente = Cliente.objects.get(pk=cliente_id)
        prestador_serv = PrestadorServicios.objects.get(pk=prestador_serv_id)
        local = Local.objects.get(pk=local_id)

        cita = Cita.objects.create(
            cliente=cliente,
            prestador_serv=prestador_serv,
            local=local,
            **validated_data
        )

        metodo_pago = validated_data.get('metodo_pago')
        monto_total = validated_data.get('monto_total')
        if metodo_pago and monto_total is not None:
            try:
                boleta = Boleta.objects.create(
                    cita=cita,
                    monto_total=monto_total,
                    metodo_pago=metodo_pago,
                    transaccion_id=str(uuid4())
                )
                HistorialCompra.objects.create(boleta=boleta, calificacion=0)
            except Exception as e:
                raise serializers.ValidationError(
                    {'boleta': f'Failed to create boleta: {str(e)}'})

        return cita

# SERIAlIZADOR QUE MANEJA LOS PRODUCTOS


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['prod_id', 'nombre_prod', 'foto', 'cantidad',
                  'a_la_venta', 'precio', 'precio_venta', 'descripcion', 'sku_id', 'local']

    def create(self, validated_data):
        producto = Producto.objects.create(**validated_data)
        return producto

    def update(self, instance, validated_data):
        instance.nombre_prod = validated_data.get(
            'nombre_prod', instance.nombre_prod)
        instance.foto = validated_data.get('foto', instance.foto)
        instance.cantidad = validated_data.get('cantidad', instance.cantidad)
        instance.a_la_venta = validated_data.get(
            'a_la_venta', instance.a_la_venta)
        instance.precio = validated_data.get('precio', instance.precio)
        instance.precio_venta = validated_data.get(
            'precio_venta', instance.precio_venta)
        instance.descripcion = validated_data.get(
            'descripcion', instance.descripcion)
        instance.sku_id = validated_data.get('sku_id', instance.sku_id)
        instance.local = validated_data.get('local', instance.local)
        instance.save()
        return instance


# SERIALIZERS DE BOLETA Y HISTORIAL DE COMPRA - CITAS


# BOLETA

class BoletaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boleta
        fields = ['boleta_id', 'fecha_emision', 'monto_total',
                  'metodo_pago', 'transaccion_id', 'cita']

    def create(self, validated_data):
        cita_id = validated_data.pop('cita')
        cita = Cita.objects.get(cita_id=cita_id)
        boleta = Boleta.objects.create(cita=cita, **validated_data)
        return boleta

    def update(self, instance, validated_data):
        instance.monto_total = validated_data.get(
            'monto_total', instance.monto_total)
        instance.metodo_pago = validated_data.get(
            'metodo_pago', instance.metodo_pago)
        instance.transaccion_id = validated_data.get(
            'transaccion_id', instance.transaccion_id)
        instance.save()
        return instance


# HISTORIAL

class HistorialCompraSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialCompra
        fields = ['hist_id', 'calificacion', 'boleta', 'fecha_registro']
