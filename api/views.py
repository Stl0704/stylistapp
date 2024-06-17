from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import views, viewsets, status, permissions, serializers
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from .serializer import UsuarioPrestadorSerializer, LocalSerializer, UsuarioClienteSerializer,  ServicioAPrestarSerializer,  ProductoSerializer, CitaSerializer, BoletaSerializer
from .models import Usuario, PrestadorServicios, ServicioAPrestar, Cita, Producto, Boleta, HistorialCompra
from .backends import UsuarioBackend
from rest_framework_simplejwt.tokens import RefreshToken


# FUNCION CREAR USUARIO - PRESTADOR


@api_view(['POST'])
@permission_classes([AllowAny])
def registrar_usuario_prestador(request):
    serializer = UsuarioPrestadorSerializer(data=request.data)
    if serializer.is_valid():
        try:
            usuario = serializer.save()
            response_data = {
                'usuario_id': usuario.user_id,
                'nombre_usuario': usuario.user_name,
                'persona_id': usuario.personausuario_set.first().persona.persona_id
            }

            if usuario.tipo_usuario == 'cliente':
                # Suponiendo que cliente es una relación OneToOne
                response_data['cliente_id'] = usuario.cliente.pk
            elif usuario.tipo_usuario == 'prestador':
                # Suponiendo que prestador_servicios es una relación OneToOne
                response_data['prestador_serv_id'] = usuario.prestadorservicios.pk

            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# CREAR LOCAL SI ES UN USUARIO PRESTADOR


@api_view(['POST'])
@permission_classes([AllowAny])
def crear_local(request):
    prestador_id = request.data.get('prestador_id')
    if not prestador_id:
        return Response({'error': 'Prestador ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        prestador = PrestadorServicios.objects.get(usuario_ptr_id=prestador_id)
    except PrestadorServicios.DoesNotExist:
        return Response({'error': 'Prestador not found'}, status=status.HTTP_404_NOT_FOUND)

    local_data = {
        'nombre': request.data.get('nombre'),
        'direccion': request.data.get('direccion'),
        'prestador': prestador.usuario_ptr_id,
        'comuna': request.data.get('comuna'),
    }

    serializer = LocalSerializer(data=local_data, context={'request': request})
    if serializer.is_valid():
        local = serializer.save()
        return Response({
            'message': 'Local creado con éxito',
            'local_id': local.pk,
            'nombre': local.nombre,
            'direccion': local.direccion
        }, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 # FUNCION CREAR USUARIO - CLIENTE


@api_view(['POST'])
# Permite a cualquier usuario hacer una petición POST
@permission_classes([AllowAny])
def registrar_usuario_cliente(request):
    serializer = UsuarioClienteSerializer(data=request.data)
    if serializer.is_valid():
        try:
            usuario = serializer.save()
            response_data = {
                'usuario_id': usuario.user_id,
                'nombre_usuario': usuario.user_name,
                'persona_id': usuario.personausuario_set.first().persona.persona_id,
                'cliente_id': usuario.pk,
                'puntos': usuario.puntos  # puntos iniciales
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# FUNCION INICIO SESION

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
            'tipo_usuario': user.tipo_usuario,
            'user_id': user.user_id,
            'user_name': user.user_name,
            'email': user.email,
        }, status=status.HTTP_200_OK)

    else:
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)


# REGISTRO DE SERVICIOS A PRESTAR:

class ServicioAPrestarView(views.APIView):
    # Asigna permisos según sea necesario, por ejemplo, sólo los usuarios autenticados pueden crear o actualizar

    def post(self, request, *args, **kwargs):
        serializer = ServicioAPrestarSerializer(data=request.data)
        if serializer.is_valid():
            servicio_prestar = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            servicio_id = request.data.get('id')
            servicio_prestar = ServicioAPrestar.objects.get(pk=servicio_id)
        except ServicioAPrestar.DoesNotExist:
            return Response({'message': 'Servicio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        # partial=True permite actualizaciones parciales
        serializer = ServicioAPrestarSerializer(
            servicio_prestar, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# LISTADO DE PRODUCTOS

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer


# FUNCIONES DE PRODUCTO

# INGRESO DE PRODUCTO
@api_view(['POST'])
@permission_classes([AllowAny])
def crear_producto(request):
    serializer = ProductoSerializer(data=request.data)
    if serializer.is_valid():
        producto = serializer.save()
        return Response(ProductoSerializer(producto).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ELIMINAR PRODUCTO
@api_view(['DELETE'])
@permission_classes([AllowAny])
def eliminar_producto(request, prod_id):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({'error': 'user_id es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(pk=user_id)
        if usuario.tipo_usuario != 'prestador':
            return Response({'error': 'Acceso denegado. Solo los prestadores pueden eliminar productos.'}, status=status.HTTP_403_FORBIDDEN)

        producto = Producto.objects.get(pk=prod_id)
        if producto.local.prestador.usuario_ptr_id != usuario.user_id:
            return Response({'error': 'No tiene permiso para eliminar este producto.'}, status=status.HTTP_403_FORBIDDEN)

        producto.delete()
        return Response({'message': 'Producto eliminado exitosamente.'}, status=status.HTTP_204_NO_CONTENT)

    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# MODIFICAR PRODUCTO
@api_view(['PATCH'])
@permission_classes([AllowAny])
def actualizar_producto(request, prod_id):
    try:
        producto = Producto.objects.get(pk=prod_id)
        usuario = Usuario.objects.get(pk=request.data.get('user_id'))
        if usuario.tipo_usuario != 'prestador':
            return Response({'error': 'Acceso denegado. Solo los prestadores pueden modificar productos.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductoSerializer(
            producto, data=request.data, partial=True)
        if serializer.is_valid():
            producto = serializer.save()
            return Response(ProductoSerializer(producto).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)


# AGENDAR CITAS

@api_view(['POST'])
@permission_classes([AllowAny])
def agendar_cita(request):
    if request.data.get('tipo_usuario') != 'cliente':
        return Response({'error': 'Solo los clientes pueden agendar citas.'}, status=status.HTTP_403_FORBIDDEN)

    serializer = CitaSerializer(data=request.data)
    if serializer.is_valid():
        try:
            cita = serializer.save()
            boleta_info = {
                'boleta_id': cita.boleta.boleta_id,
                'monto_total': cita.boleta.monto_total,
                'metodo_pago': cita.boleta.metodo_pago,
                'fecha_emision': cita.boleta.fecha_emision.strftime('%Y-%m-%d %H:%M:%S')
            } if hasattr(cita, 'boleta') and cita.boleta else 'No se pudo crear la boleta'
            return Response({'cita_id': cita.id, 'boleta_info': boleta_info}, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
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
