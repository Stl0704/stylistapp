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
                  'local', 'disponibilidad']

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


class ServicioSerializer(serializers.ModelSerializer):
    servicioaprestar = serializers.PrimaryKeyRelatedField(
        queryset=ServicioAPrestar.objects.all())
    local = serializers.PrimaryKeyRelatedField(
        queryset=Local.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Servicio
        fields = ['servicioaprestar', 'local', 'duracion_serv', 'nombre_serv',
                  'precio', 'metodo_pago', 'foto', 'descripcion', 'disponibilidad']

    def create(self, validated_data):
        return Servicio.objects.create(**validated_data)


class ServicioAPrestarSerializer(serializers.ModelSerializer):
    especialidad = serializers.CharField(max_length=350)
    prestador_serv = serializers.PrimaryKeyRelatedField(
        queryset=PrestadorServicios.objects.all())
    local = serializers.PrimaryKeyRelatedField(queryset=Local.objects.all())

    class Meta:
        model = ServicioAPrestar
        fields = ['id', 'especialidad', 'prestador_serv', 'local']

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
        fields = ['usuario_ptr_id', 'especialidad',
                  'experiencia', 'presentacion', 'calificacion']

    def create(self, validated_data):
        usuario_id = validated_data.pop('usuario_ptr_id')
        usuario = Usuario.objects.get(pk=usuario_id)
        prestador = PrestadorServicios.objects.create(
            user_ptr=usuario, **validated_data)
        return prestador


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['usuario_ptr_id', 'img', 'puntos']

    def create(self, validated_data):
        usuario_id = validated_data.pop('usuario_ptr_id')
        usuario = Usuario.objects.get(pk=usuario_id)
        cliente = Cliente.objects.create(user_ptr=usuario, **validated_data)
        return cliente


class ClienteSerializerGet(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['usuario_ptr_id', 'user_name',
                  'email', 'tipo_usuario', 'img', 'puntos']


class PrestadorServiciosSerializerGet(serializers.ModelSerializer):
    class Meta:
        model = PrestadorServicios
        fields = ['usuario_ptr_id', 'user_name', 'email', 'tipo_usuario',
                  'especialidad', 'experiencia', 'presentacion', 'calificacion']

# SERIALIZADOR LOCAL-PRESTADOR:


class LocalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Local
        fields = ['local_id', 'nombre', 'direccion', 'prestador',
                  'comuna', 'hora_apertura', 'hora_cierre']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        return Local.objects.create(**validated_data)

# GET LOCAL SERIALIZER


class LocalGet(serializers.ModelSerializer):
    class Meta:
        model = Local
        fields = ['local_id', 'nombre', 'direccion', 'prestador',
                  'comuna', 'hora_apertura', 'hora_cierre']

# COMUNA


class ComunaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comuna
        fields = ['id', 'nombre', 'poblacion', 'area']

# SERIALIZADOR CITAS:

#          PETICION:


#  OJO: LA PETICION DE "PRODUCTOS" SIEMPRE ESPERA UN RANGO EN LISTA ([])


# {
#     "tipo_usuario": "cliente",
#     "cliente_id": 23,
#     "prestador_serv_id": 3,
#     "local_id": 1,
#     "productos": [],
#     "fecha_hora": "2024-06-30",
#     "duracion": "01:00:00",
#     "metodo_pago": "tarjeta",
#     "monto_total": 120.00
# }


# PETICION CON LISTA DE PRODUCTOS:

# {
#   "fecha_hora": "2024-07-01T10:00:00Z",
#   "duracion": "01:00:00",
#   "cliente_id": 23,
#   "prestador_serv_id": 1,
#   "local_id": 1,
#   "metodo_pago": "tarjeta",
#   "monto_total": 15000.00,
#   "productos": [
#     {
#       "nombre": "Cepillo de pelo",
#       "precio": 90000,
#       "cantidad": 2
#     }
#   ],
#   "tipo_usuario": "cliente"
# }


class CitaSerializer(serializers.ModelSerializer):
    cliente_id = serializers.IntegerField(write_only=True)
    prestador_serv_id = serializers.IntegerField(write_only=True)
    local_id = serializers.IntegerField(write_only=True)
    metodo_pago = serializers.CharField(max_length=45, write_only=True)
    monto_total = serializers.DecimalField(
        max_digits=10, decimal_places=2, write_only=True)
    # Campo para manejar productos en formato JSON
    productos = serializers.JSONField()

    class Meta:
        model = Cita
        fields = ['fecha_hora', 'duracion', 'cliente_id',
                  'prestador_serv_id', 'local_id', 'metodo_pago', 'monto_total', 'productos']

    @transaction.atomic
    def create(self, validated_data):
        cliente_id = validated_data.pop('cliente_id')
        prestador_serv_id = validated_data.pop('prestador_serv_id')
        local_id = validated_data.pop('local_id')
        productos = validated_data.pop('productos')

        cliente = Cliente.objects.get(pk=cliente_id)
        prestador_serv = PrestadorServicios.objects.get(pk=prestador_serv_id)
        local = Local.objects.get(pk=local_id)

        cita = Cita.objects.create(
            cliente=cliente,
            prestador_serv=prestador_serv,
            local=local,
            productos=productos,
            fecha_hora=validated_data['fecha_hora'],
            duracion=validated_data['duracion']
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

    def validate_productos(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Productos debe ser una lista.")
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    "Cada producto debe ser un diccionario.")
            required_keys = {'nombre', 'precio', 'cantidad'}
            if not required_keys.issubset(item.keys()):
                raise serializers.ValidationError(
                    f"Cada producto debe contener las claves: {required_keys}")
        return value

# Serializador de inventario


class InventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventario
        fields = ['inv_id', 'nombre_lista', 'local']

    def create(self, validated_data):
        return Inventario.objects.create(**validated_data)

# SERIAlIZADOR QUE MANEJA LOS PRODUCTOS


# SERIAlIZADOR QUE MANEJA LOS PRODUCTOS
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = [
            'prod_id', 'nombre_producto', 'foto', 'cantidad', 'a_la_venta',
            'precio_compra', 'precio_venta_x_mayor', 'precio_venta_x_menor',
            'descripcion', 'sku_id', 'inventario', 'local'
        ]

    def validate(self, data):
        if data['a_la_venta']:
            if not data.get('precio_venta_x_mayor') or not data.get('precio_venta_x_menor'):
                raise serializers.ValidationError(
                    "Los precios de venta al por mayor y menor son obligatorios cuando el producto está a la venta.")
        return data

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

# GET PRODUCTOS:


class ProductoGet(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['prod_id', 'nombre_prod', 'foto', 'cantidad', 'a_la_venta',
                  'precio', 'precio_venta', 'descripcion', 'sku_id', 'local']

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


class CitaDetalleSerializer(serializers.ModelSerializer):
    # Esto mostrará el nombre del cliente en lugar del ID
    cliente = serializers.StringRelatedField()
    # Esto mostrará el nombre del prestador en lugar del ID
    prestador_serv = serializers.StringRelatedField()
    # Esto mostrará el nombre del local en lugar del ID
    local = serializers.StringRelatedField()

    class Meta:
        model = Cita
        fields = ['cita_id', 'fecha_hora', 'duracion',
                  'cliente', 'prestador_serv', 'local', 'productos']


class BoletaDetalleSerializer(serializers.ModelSerializer):
    cita = CitaDetalleSerializer()  # Anidar el serializador de Cita

    class Meta:
        model = Boleta
        fields = ['boleta_id', 'cita', 'fecha_emision',
                  'monto_total', 'metodo_pago', 'transaccion_id']


class HistorialCompraDetalleSerializer(serializers.ModelSerializer):
    boleta = BoletaDetalleSerializer()  # Anidar el serializador de Boleta

    class Meta:
        model = HistorialCompra
        fields = ['hist_id', 'calificacion', 'boleta', 'fecha_registro']
