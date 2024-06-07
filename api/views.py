from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import AllowAny
from .serializer import UsuarioPersonaSerializer,  PrestadorServiciosSerializer,  ProductoSerializer, CitaSerializer
from .models import Usuario, Persona, PrestadorServicios, Cliente, ServicioAPrestar, Cita, Producto
from .backends import UsuarioBackend
from rest_framework_simplejwt.tokens import RefreshToken


# FUNCION CREAR USUARIO - PERSONA


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def registrar_usuario_persona(request):
    serializer = UsuarioPersonaSerializer(data=request.data)
    if serializer.is_valid():
        try:
            usuario, persona = serializer.save()
            response_data = {
                'usuario_id': usuario.user_id,
                'nombre_usuario': usuario.user_name,
                'persona_id': persona.persona_id
            }
            if usuario.tipo_usuario == 'cliente':
                response_data['cliente_id'] = Cliente.objects.get(
                    user_ptr=usuario).pk
            elif usuario.tipo_usuario == 'prestador':
                response_data['prestador_serv_id'] = PrestadorServicios.objects.get(
                    user_ptr=usuario).pk
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def iniciar_sesion(request):
    user_name = request.data.get('user_name')
    password = request.data.get('password')
    user = UsuarioBackend().authenticate(
        request, username=user_name, password=password)

    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.user_id,
            'user_name': user.user_name,
            'email': user.email,
        }, status=status.HTTP_200_OK)

    else:
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)


# LISTADO DE PRODUCTOS

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer


# AGENDAR CITAS

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def agendar_cita(request):
    tipo_usuario = request.data.get('tipo_usuario', None)
    if tipo_usuario != 'cliente':
        return Response({'error': 'Solo los clientes pueden agendar citas.'}, status=status.HTTP_403_FORBIDDEN)

    cliente_id = request.data.get('cliente_id')
    prestador_serv_id = request.data.get('prestador_serv_id')

    try:
        cliente = Usuario.objects.get(tipo_usuario=cliente_id)
    except Usuario.DoesNotExist:
        return Response({'error': 'Cliente no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        prestador_serv = Usuario.objects.get(
            tipo_usuario=prestador_serv_id)
    except PrestadorServicios.DoesNotExist:
        return Response({'error': 'Prestador de servicios no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CitaSerializer(data=request.data)
    if serializer.is_valid():
        try:
            cita = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# RETRASAR CITAS


@api_view(['PATCH'])
@permission_classes([permissions.AllowAny])
def retrasar_cita(request, cita_id):
    try:
        cita = Cita.objects.get(cita_id=cita_id)
    except Cita.DoesNotExist:
        return Response({'error': 'Cita no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    if request.user.tipo_usuario != 'prestador':
        return Response({'error': 'Solo los prestadores pueden solicitar un retraso.'}, status=status.HTTP_403_FORBIDDEN)

    nueva_fecha_hora = request.data.get('nueva_fecha_hora')
    if not nueva_fecha_hora:
        return Response({'error': 'Debe proporcionar la nueva fecha y hora.'}, status=status.HTTP_400_BAD_REQUEST)

    cita.fecha_hora = nueva_fecha_hora
    cita.save()
    return Response({'message': 'Cita retrasada exitosamente.'}, status=status.HTTP_200_OK)
