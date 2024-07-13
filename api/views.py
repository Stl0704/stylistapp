from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework import status, generics, filters, views, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from .models import *
from .serializer import *
from .backends import UsuarioBackend
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
import logging
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


@api_view(['POST'])
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
                'puntos': usuario.puntos
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
                'persona_id': usuario.personausuario_set.first().persona.persona_id,
                'prestador_serv_id': usuario.prestadorservicios.pk
            }
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
        user_data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'tipo_usuario': user.tipo_usuario,
            'user_id': user.user_id,
            'user_name': user.user_name,
            'email': user.email,
        }

        # Adding the additional data
        user_data['persona_nombre'] = user.personausuario_set.first(
        ).persona.nombre if user.personausuario_set.exists() else None
        user_data['local_id'] = user.local.local_id if user.tipo_usuario == 'prestador' and hasattr(
            user, 'local') else None

        return Response(user_data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

# CITAS

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
            return Response({'cita_id': cita.cita_id, 'boleta_info': boleta_info}, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET CITAS

@api_view(['GET'])
@permission_classes([AllowAny])
def listar_citas(request):

    citas = Cita.objects.all()
    serializer = CitaSerializer(citas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# GET POR LOCAL


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_citas_por_local(request):

    # Obtiene el ID del local desde los parámetros de la consulta
    local_id = request.query_params.get('local_id')
    if local_id is not None:
        # Filtra las citas por local
        citas = Cita.objects.filter(local__id=local_id)
        serializer = CitaSerializer(citas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'No se proporcionó un local_id válido.'}, status=status.HTTP_400_BAD_REQUEST)

# RETRASAR CITAS


@api_view(['PATCH'])
@permission_classes([AllowAny])
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


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_citas_cliente(request, cliente_id):
    citas = Cita.objects.filter(cliente_id=cliente_id)
    serializer = CitaSerializer(citas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_citas_prestador(request, prestador_id):
    citas = Cita.objects.filter(prestador_serv_id=prestador_id)
    serializer = CitaSerializer(citas, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_productos_por_local(request, local_id):
    try:
        local = Local.objects.get(pk=local_id)
    except Local.DoesNotExist:
        return Response({'message': 'Local no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    productos = Producto.objects.filter(local=local)
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_productos_por_inventario(request, inventario_id):
    try:
        inventario = Inventario.objects.get(pk=inventario_id)
    except Inventario.DoesNotExist:
        return Response({'message': 'Inventario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    productos = Producto.objects.filter(local=inventario.local)
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_productos(request):
    productos = Producto.objects.all()
    serializer = ProductoGet(productos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def agregar_producto(request):
    serializer = ProductoSerializer(data=request.data)
    if serializer.is_valid():
        producto = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def actualizar_producto(request, producto_id):
    try:
        producto = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        return Response({'message': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductoSerializer(producto, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def eliminar_producto(request, producto_id):
    try:
        producto = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        return Response({'message': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    producto.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_usuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if usuario.tipo_usuario == 'cliente':
        serializer = ClienteSerializerGet(usuario)
    elif usuario.tipo_usuario == 'prestador':
        serializer = PrestadorServiciosSerializerGet(usuario)
    else:
        return Response({'message': 'Tipo de usuario no reconocido'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def actualizar_usuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if usuario.tipo_usuario == 'cliente':
        serializer = UsuarioClienteSerializer(
            usuario, data=request.data, partial=True)
    elif usuario.tipo_usuario == 'prestador':
        serializer = UsuarioPrestadorSerializer(
            usuario, data=request.data, partial=True)
    else:
        return Response({'message': 'Tipo de usuario no reconocido'}, status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def eliminar_usuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    usuario.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_locales(request):
    locales = Local.objects.all()
    serializer = LocalGet(locales, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def crear_local(request):
    prestador_id = request.data.get('prestador_id')
    if not prestador_id:
        return Response({'error': 'Prestador ID es requerido'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        prestador = PrestadorServicios.objects.get(usuario_ptr_id=prestador_id)
    except PrestadorServicios.DoesNotExist:
        return Response({'error': 'Prestador no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    local_data = {
        'nombre': request.data.get('nombre'),
        'direccion': request.data.get('direccion'),
        'prestador': prestador.usuario_ptr_id,
        'comuna': request.data.get('comuna'),
        'hora_apertura': request.data.get('hora_apertura'),
        'hora_cierre': request.data.get('hora_cierre')
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


@api_view(['PATCH'])
@permission_classes([AllowAny])
def actualizar_local(request, local_id):
    try:
        local = Local.objects.get(pk=local_id)
    except Local.DoesNotExist:
        return Response({'message': 'Local no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    serializer = LocalSerializer(local, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def eliminar_local(request, local_id):
    try:
        local = Local.objects.get(pk=local_id)
    except Local.DoesNotExist:
        return Response({'message': 'Local no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    local.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_inventarios_por_local(request, local_id):
    try:
        local = Local.objects.get(pk=local_id)
    except Local.DoesNotExist:
        return Response({'message': 'Local no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    inventarios = Inventario.objects.filter(local=local)
    serializer = InventarioSerializer(inventarios, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_productos_por_inventario(request, inventario_id):
    try:
        inventario = Inventario.objects.get(pk=inventario_id)
    except Inventario.DoesNotExist:
        return Response({'message': 'Inventario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    productos = Producto.objects.filter(inventario=inventario)
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_productos_por_local(request, local_id):
    try:
        local = Local.objects.get(pk=local_id)
    except Local.DoesNotExist:
        return Response({'message': 'Local no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    productos = Producto.objects.filter(local=local)
    serializer = ProductoSerializer(productos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_inventarios(request):
    local_id = request.query_params.get('local_id')
    if local_id:
        inventarios = Inventario.objects.filter(local_id=local_id)
    else:
        inventarios = Inventario.objects.all()
    serializer = InventarioSerializer(inventarios, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def agregar_inventario(request):
    serializer = InventarioSerializer(data=request.data)
    if serializer.is_valid():
        inventario = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def actualizar_inventario(request, inventario_id):
    try:
        inventario = Inventario.objects.get(pk=inventario_id)
    except Inventario.DoesNotExist:
        return Response({'message': 'Inventario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    serializer = InventarioSerializer(
        inventario, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def eliminar_inventario(request, inventario_id):
    try:
        inventario = Inventario.objects.get(pk=inventario_id)
    except Inventario.DoesNotExist:
        return Response({'message': 'Inventario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    inventario.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_producto(request, producto_id):
    try:
        producto = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        return Response({'message': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductoGet(producto)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_local(request, local_id):
    try:
        local = Local.objects.get(pk=local_id)
    except Local.DoesNotExist:
        return Response({'message': 'Local no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    serializer = LocalGet(local)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_servicio(request, servicio_id):
    try:
        servicio = Servicio.objects.get(pk=servicio_id)
    except Servicio.DoesNotExist:
        return Response({'message': 'Servicio no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ServicioSerializer(servicio)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_inventario_detalle(request, inventario_id):
    try:
        inventario = Inventario.objects.get(pk=inventario_id)
    except Inventario.DoesNotExist:
        return Response({'message': 'Inventario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    productos = Producto.objects.filter(local=inventario.local)
    serializer = ProductoGet(productos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def realizar_compra(request):
    return Response({'message': 'Compra realizada con éxito'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_comunas(request):
    try:
        comunas = Comuna.objects.all()
        serializer = ComunaSerializer(comunas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def ver_historial_compras(request, cliente_id):
    try:
        historial = HistorialCompra.objects.filter(boleta__cita__cliente_id=cliente_id).select_related(
            'boleta', 'boleta__cita', 'boleta__cita__cliente', 'boleta__cita__prestador_serv', 'boleta__cita__local')

        if not historial.exists():
            logger.info(
                f"No se encontraron registros para cliente_id={cliente_id}")
            return Response([], status=status.HTTP_200_OK)

        logger.info(
            f"Historial encontrado: {historial.count()} registros para cliente_id={cliente_id}")
        serializer = HistorialCompraDetalleSerializer(historial, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error al obtener historial de compras: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listar_servicios_aprestar(request):
    servicios = ServicioAPrestar.objects.all()
    serializer = ServicioAPrestarSerializer(servicios, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def listar_servicios_por_local(request, local_id):
    servicios = ServicioAPrestar.objects.filter(local=local_id)
    serializer = ServicioAPrestarSerializer(servicios, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def obtener_servicio_aprestar(request, id):
    servicio = get_object_or_404(ServicioAPrestar, pk=id)
    serializer = ServicioAPrestarSerializer(servicio)
    return Response(serializer.data)


@api_view(['POST'])
def crear_servicio_aprestar(request):
    serializer = ServicioAPrestarSerializer(data=request.data)
    if serializer.is_valid():
        prestador_serv_id = request.data['prestador_serv']
        especialidad = request.data.get('especialidad', '')

        # Verificar si ya existe la misma especialidad para este prestador
        if ServicioAPrestar.objects.filter(prestador_serv=prestador_serv_id, especialidad=especialidad).exists():
            return Response(
                {"error": "Esta especialidad ya existe para este prestador de servicios."},
                status=status.HTTP_401_BAD_REQUEST
            )

        # Verificar si el prestador ya tiene el máximo de especialidades permitidas
        if ServicioAPrestar.objects.filter(prestador_serv=prestador_serv_id).count() >= 7:
            return Response(
                {"error": "El prestador de servicios ya tiene el máximo de 7 especialidades permitidas."},
                status=status.HTTP_402_BAD_REQUEST
            )

        # Guardar el nuevo servicio a prestar si pasa las validaciones
        servicio_aprestar = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Manejar errores de validación del serializer
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
def actualizar_servicio_aprestar(request, id):
    servicio = get_object_or_404(ServicioAPrestar, pk=id)
    serializer = ServicioAPrestarSerializer(
        servicio, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def eliminar_servicio_aprestar(request, id):
    try:
        servicio = ServicioAPrestar.objects.get(id=id)
        servicio.delete()
        return Response(status=204)
    except ServicioAPrestar.DoesNotExist:
        return Response(status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def listar_servicios(request):
    servicios = Servicio.objects.all()
    serializer = ServicioSerializer(servicios, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def crear_servicio(request):
    serializer = ServicioSerializer(data=request.data)
    if serializer.is_valid():
        servicio = serializer.save()
        return Response(ServicioSerializer(servicio).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def eliminar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, pk=servicio_id)
    servicio.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def obtener_servicios_por_local(request, local_id):
    try:
        servicios = Servicio.objects.filter(local_id=local_id)
        serializer = ServicioSerializer(servicios, many=True)
        return Response(serializer.data)
    except Local.DoesNotExist:
        return Response({'error': 'Local no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
# Asegúrate que el nombre del parámetro sea correcto
def obtener_servicios_por_servicioaprestar(request, servicioaprestar_id):
    try:
        servicios = Servicio.objects.filter(
            servicioaprestar__id=servicioaprestar_id)
        serializer = ServicioSerializer(servicios, many=True)
        return Response(serializer.data)
    except Local.DoesNotExist:
        return Response({'error': 'Local no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def actualizar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, pk=servicio_id)
    serializer = ServicioSerializer(servicio, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
