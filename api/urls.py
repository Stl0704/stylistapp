from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (registrar_usuario_prestador, crear_local, registrar_usuario_cliente, iniciar_sesion,
                    ProductoViewSet, agendar_cita, retrasar_cita, ServicioAPrestarView,
                    crear_producto, eliminar_producto, actualizar_producto)

router = DefaultRouter()
router.register(r'productos', ProductoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('registrarp/', registrar_usuario_prestador,
         name='registrar_usuario_prestador'),
    path('local/', crear_local, name='crear_local'),
    path('registrarc/', registrar_usuario_cliente, name='registrar_cliente'),
    path('login/', iniciar_sesion, name='iniciar_sesion'),
    path('agendar_cita/', agendar_cita, name='agendar_cita'),
    path('retrasar_cita/<int:cita_id>/', retrasar_cita, name='retrasar_cita'),
    path('servicio/', ServicioAPrestarView.as_view(), name='gestion_servicio'),
    path('producto/crear/', crear_producto, name='crear_producto'),
    path('producto/eliminar/<int:prod_id>/',
         eliminar_producto, name='eliminar_producto'),
    path('producto/actualizar/<int:prod_id>/',
         actualizar_producto, name='actualizar_producto'),
]
