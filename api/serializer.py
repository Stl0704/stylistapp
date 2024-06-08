from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import *


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

# PRODUCTO:


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


# FUNCIONES:


# PETICION INICIO SESION

# {
#   "user_name": "JohnDoe",
#   "password": "12345678"
# }

# REGISTRO DE PRODUCTO

# {
#     "nombre_prod": "",
#     "foto": "",
#     "cantidad": null,
#     "a_la_venta": false,
#     "precio": null,
#     "descripcion": "",
#     "sku_id": "",
#     "local": null
# }

# SOLICITUD CREACION USUARIO PRESTADOR DE SERVICIOS

# {
#     "user_name": " Mario_Cliente",
#     "email": "cliente@example.com",
#     "password": "12345678",
#     "nombre": "Mario",
#     "apellido1": "Fica",
#     "apellido2": "Sanchez",
#     "fecha_nac": "1993-09-14",
#     "genero_id": 2,
#     "tipo_usuario": "prestador",
#     "especialidad": "quiropractica terapéutica",
#     "experiencia": "7 años",
#     "presentacion": "Especialista en terapias de relajación y rehabilitación",
#     "calificacion": 4.5
# }


# Serializer Crear Usuario

class UsuarioPersonaSerializer(serializers.Serializer):
    # Datos de Usuario
    user_name = serializers.CharField(max_length=45)
    email = serializers.EmailField(max_length=45)
    password = serializers.CharField(max_length=128, write_only=True)
    tipo_usuario = serializers.ChoiceField(
        choices=Usuario.tipo_usuario.field.choices)

    # Datos de Persona
    nombre = serializers.CharField(max_length=55)
    apellido1 = serializers.CharField(max_length=30)
    apellido2 = serializers.CharField(max_length=30)
    fecha_nac = serializers.DateField()
    genero_id = serializers.PrimaryKeyRelatedField(
        queryset=Genero.objects.all(), write_only=True)

    # Campos específicos para Cliente
    img = serializers.CharField(
        max_length=350, required=False, allow_blank=True)
    puntos = serializers.IntegerField(required=False, default=0)

    # Campos específicos para PrestadorServicios
    especialidad = serializers.CharField(
        max_length=350, required=False, allow_blank=True)
    experiencia = serializers.CharField(
        max_length=450, required=False, allow_blank=True)
    presentacion = serializers.CharField(
        max_length=200, required=False, allow_blank=True)
    calificacion = serializers.DecimalField(
        max_digits=3, decimal_places=2, required=False, allow_null=True)

    # Campos para la Cita (si es cliente)
    cita_fecha_hora = serializers.DateTimeField(required=False)
    cita_duracion = serializers.TimeField(required=False)
    cita_local_id = serializers.PrimaryKeyRelatedField(
        queryset=Local.objects.all(), write_only=True, required=False)

    def create(self, validated_data):
        # Extraer y eliminar genero de los datos validados
        genero = validated_data.pop('genero_id')

        # Crear la Persona
        persona_data = {
            'nombre': validated_data.pop('nombre'),
            'apellido1': validated_data.pop('apellido1'),
            'apellido2': validated_data.pop('apellido2'),
            'fecha_nac': validated_data.pop('fecha_nac'),
            'genero': genero
        }
        persona = Persona.objects.create(**persona_data)

        # Crear el Usuario y hashear la contraseña usando el método del modelo
        usuario_data = {
            'user_name': validated_data.pop('user_name'),
            'email': validated_data.pop('email'),
            'tipo_usuario': validated_data.pop('tipo_usuario')
        }
        usuario = Usuario(**usuario_data)
        usuario.set_password(validated_data.pop('password'))
        usuario.save()

        # Crear la relación PersonaUsuario
        PersonaUsuario.objects.create(persona=persona, user=usuario)

        # Dependiendo del tipo de usuario, crea el perfil correspondiente
        if usuario.tipo_usuario == 'cliente':
            cliente = Cliente.objects.create(
                user_ptr=usuario,
                img=validated_data.get('img', ''),
                puntos=validated_data.get('puntos', 0)
            )

            # Registrar una cita si se proporcionan los datos necesarios
            if 'cita_fecha_hora' in validated_data and 'cita_duracion' in validated_data and 'cita_local_id' in validated_data:
                Cita.objects.create(
                    prestador_serv=None,  # Esto debe actualizarse según la lógica de la aplicación
                    cliente=cliente,
                    fecha_hora=validated_data.get('cita_fecha_hora'),
                    duracion=validated_data.get('cita_duracion'),
                    local=validated_data.get('cita_local_id')
                )

        elif usuario.tipo_usuario == 'prestador':
            PrestadorServicios.objects.create(
                user_ptr=usuario,
                especialidad=validated_data.get('especialidad', ''),
                experiencia=validated_data.get('experiencia', ''),
                presentacion=validated_data.get('presentacion', ''),
                calificacion=validated_data.get('calificacion', 0)
            )

        return usuario, persona


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

# REGISTRO DE SERVICIOS


class ServicioAPrestarSerializer(serializers.ModelSerializer):
    # Usa StringRelatedField o PrimaryKeyRelatedField según prefieras representar los datos
    servicio = serializers.PrimaryKeyRelatedField(
        queryset=Servicio.objects.all())
    prestador_serv = serializers.PrimaryKeyRelatedField(
        queryset=PrestadorServicios.objects.all())
    local = serializers.PrimaryKeyRelatedField(queryset=Local.objects.all())

    class Meta:
        model = ServicioAPrestar
        fields = ['servicio', 'prestador_serv',
                  'local', 'tarifa', 'disponibilidad']

    def create(self, validated_data):
        # Crear instancia de ServicioAPrestar con los datos validados
        servicio_a_prestar = ServicioAPrestar.objects.create(**validated_data)
        return servicio_a_prestar

    def update(self, instance, validated_data):
        # Actualizar instancia existente de ServicioAPrestar
        instance.servicio = validated_data.get('servicio', instance.servicio)
        instance.prestador_serv = validated_data.get(
            'prestador_serv', instance.prestador_serv)
        instance.local = validated_data.get('local', instance.local)
        instance.tarifa = validated_data.get('tarifa', instance.tarifa)
        instance.disponibilidad = validated_data.get(
            'disponibilidad', instance.disponibilidad)
        instance.save()
        return instance


# SERIALIZADOR CITAS:

class CitaSerializer(serializers.ModelSerializer):
    cliente_id = serializers.IntegerField(write_only=True)
    prestador_serv_id = serializers.IntegerField(write_only=True)
    local_id = serializers.PrimaryKeyRelatedField(
        queryset=Local.objects.all(), write_only=True)

    class Meta:
        model = Cita
        fields = ['cita_id', 'prestador_serv_id',
                  'cliente_id', 'fecha_hora', 'duracion', 'local_id']

    def create(self, validated_data):
        cliente_id = validated_data.pop('cliente_id')
        prestador_serv_id = validated_data.pop('prestador_serv_id')
        local = validated_data.pop('local_id')

        cliente = Cliente.objects.get(user_id=cliente_id)
        prestador_serv = PrestadorServicios.objects.get(
            user_id=prestador_serv_id)

        cita = Cita.objects.create(
            cliente=cliente, prestador_serv=prestador_serv, local=local, **validated_data)
        return cita
