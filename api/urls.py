from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (registrar_usuario_prestador, crear_local, registrar_usuario_cliente, iniciar_sesion, ProductoViewSet, agendar_cita,
                    retrasar_cita, ServicioAPrestarView, crear_producto, eliminar_producto, actualizar_producto, obtener_datos_usuario, obtener_productos, obtener_locales, ver_historial_compras, listar_comunas, PrestadorServiciosListView, PrestadorServiciosDetailView, ServicioAPrestarListView, ServicioAPrestarDetailView)


router = DefaultRouter()
router.register(r'productos', ProductoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('registrarp/', registrar_usuario_prestador,
         name='registrar_usuario_prestador'),
    path('local/', crear_local, name='crear_local'),
    path('registrarc/', registrar_usuario_cliente, name='registrar_cliente'),
    path('login/', iniciar_sesion, name='iniciar_clearsesion'),
    path('get_user/', obtener_datos_usuario, name='obtener_datos_usuario'),
    path('agendar_cita/', agendar_cita, name='agendar_cita'),
    path('ver_historial_compras/<int:cliente_id>/',
         ver_historial_compras, name='ver_historial_compras'),
    path('retrasar_cita/<int:cita_id>/', retrasar_cita, name='retrasar_cita'),
    path('servicio/', ServicioAPrestarView.as_view(), name='gestion_servicio'),
    path('producto/crear/', crear_producto, name='crear_producto'),
    path('producto/eliminar/<int:prod_id>/',
         eliminar_producto, name='eliminar_producto'),
    path('producto/actualizar/<int:prod_id>/',
         actualizar_producto, name='actualizar_producto'),
    path('productoGet/', obtener_productos, name='obtener_productos'),
    path('localGet/', obtener_locales, name='obtener_locales'),
    path('comunas/', listar_comunas, name='listar_comunas'),
    path('prestadores/', PrestadorServiciosListView.as_view(),
         name='prestador_servicios_list'),
    path('prestadores/<int:pk>/', PrestadorServiciosDetailView.as_view(),
         name='prestador_servicios_detail'),
    path('servicios_a_prestar/', ServicioAPrestarListView.as_view(),
         name='servicio_a_prestar_list'),
    path('servicios_a_prestar/<int:id>/',
         ServicioAPrestarDetailView.as_view(), name='servicio_a_prestar_detail'),


]
