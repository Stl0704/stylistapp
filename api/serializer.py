from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import *

# SERIALIZADORES PARA INICIO REGISTRO Y ACTUALIZACION DE DATOS DEL USUARIO.


class UsurarioInicio(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'
            
class UsuarioRegistro(serializers.ModelSerializer):
    class Meta:
        model = Persona,Usuario
        fields = '__all__'
        
class UsuarioUpdate(serializers.ModelSerializer):
    class Meta:
        model = Persona,Usuario
        fields = '__all__'
        read_only_fields = ('user_name', 'password', 'email','nombre','apellido1','apellido2','genero')
            
class UsuarioCliente(serializers.ModelSerializer):
    class Meta:
        model = Persona, Usuario,TipoUsuario
        fields = '__all__'
        
class UsuarioEstilista(serializers.ModelSerializer):
    class Meta:
        model = Persona,Usuario,TipoUsuario
        fields = '__all__'
        
        
# SERIALIZADORES PARA persona


class PersonaInicio(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = '__all__'

# PRUEBAS:
#

#GENERO
class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = ['genero_id', 'nombre', 'descripcion']

#PERSONA
class PersonaSerializer(serializers.ModelSerializer):
    genero = GeneroSerializer(read_only=True)
    genero_id = serializers.PrimaryKeyRelatedField(
        queryset=Genero.objects.all(), source='genero', write_only=True
    )

    class Meta:
        model = Persona
        fields = ['persona_id', 'fecha_nac', 'genero', 'genero_id', 'nombre', 'apellido1', 'apellido2']

#USUARIO

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['user_id', 'user_name', 'email', 'password']

#TIPO USUARIO

class TipoUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoUsuario
        fields = ['tipo_user_id', 'nombre_tipo_user', 'descripcion']

#PERSONA USUARIO

class PersonaUsuarioSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer(read_only=True)
    user = UsuarioSerializer(read_only=True)
    tipo_user = TipoUsuarioSerializer(read_only=True)

    class Meta:
        model = PersonaUsuario
        fields = ['persona_user_id', 'persona', 'user', 'tipo_user']

# CLIENTE

class ClienteSerializer(serializers.ModelSerializer):
    user = UsuarioSerializer(read_only=True)

    class Meta:
        model = Cliente
        fields = ['cliente_id', 'user']


# PRESTADOR DE SERVICIOS

class PrestadorServiciosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrestadorServicios
        fields = ['prestador_serv_id', 'user', 'especialidad', 'experiencia', 'presentacion', 'calificacion']


# SERVICIO A PRESTAR

class ServicioAPrestarSerializer(serializers.ModelSerializer):
    servicio = serializers.StringRelatedField()
    prestador_serv = PrestadorServiciosSerializer(read_only=True)
    local = serializers.StringRelatedField()

    class Meta:
        model = ServicioAPrestar
        fields = ['servicio', 'prestador_serv', 'local', 'tarifa', 'disponibilidad']

# CITA

class CitaSerializer(serializers.ModelSerializer):
    prestador_serv = PrestadorServiciosSerializer(read_only=True)
    cliente = ClienteSerializer(read_only=True)
    servicio = serializers.StringRelatedField()
    local = serializers.StringRelatedField()

    class Meta:
        model = Cita
        fields = ['cita_id', 'prestador_serv', 'cliente', 'servicio', 'fecha_hora', 'duracion', 'local']

# DISTRITO

class DistritoSerializer(serializers.ModelSerializer):
    local = serializers.StringRelatedField()

    class Meta:
        model = Distrito
        fields = ['distrito_id', 'nombre_distrito', 'local']


## FUNCIONES:

# CREAR PERSONA-USUARIO

    
    # PETICION JSON
    
#     {
#     "user_name": "mario",
#     "email": "mariohash@123.com",
#     "password": "12345678",
#     "nombre": "lalo hash",
#     "apellido1": "landa",
#     "apellido2": "landa",
#     "fecha_nac": "2004-11-13",
#     "genero_id": 2,
#     "tipo_user_id": 1
# }

#PETICION INICIO SESION

# {
#   "user_name": "lalo",
#   "password": "12345678"
# }








# Serializer Crear Usuario-Persona

class UsuarioPersonaSerializer(serializers.Serializer):
    # Datos de Usuario
    user_name = serializers.CharField(max_length=45)
    email = serializers.CharField(max_length=45)
    password = serializers.CharField(max_length=45, write_only=True)
    
    # Datos de Persona
    nombre = serializers.CharField(max_length=55)
    apellido1 = serializers.CharField(max_length=30)
    apellido2 = serializers.CharField(max_length=30)
    fecha_nac = serializers.DateField()
    genero_id = serializers.PrimaryKeyRelatedField(
        queryset=Genero.objects.all(), source='genero', write_only=True
    )

    # Datos de TipoUsuario
    tipo_user_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoUsuario.objects.all(), source='tipo_user', write_only=True
    )

    def create(self, validated_data):
        # Crear el Usuario
        usuario_data = {
            'user_name': validated_data['user_name'],
            'email': validated_data['email']
        }
        password = validated_data['password']
        usuario = Usuario.objects.create(**usuario_data)
        usuario.set_password(password)
        
        # Crear la Persona
        persona_data = {
            'nombre': validated_data['nombre'],
            'apellido1': validated_data['apellido1'],
            'apellido2': validated_data['apellido2'],
            'fecha_nac': validated_data['fecha_nac'],
            'genero': validated_data['genero']
        }
        persona = Persona.objects.create(**persona_data)
        
        # Crear la relación PersonaUsuario
        persona_usuario = PersonaUsuario.objects.create(
            persona=persona, 
            user=usuario, 
            tipo_user=validated_data['tipo_user']
        )

        return usuario, persona, persona_usuario


#serializer de inicio sesion:

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