from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (registrar_usuario_persona, iniciar_sesion,
                    ProductoViewSet, agendar_cita, retrasar_cita)


router = DefaultRouter()
router.register(r'productos', ProductoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('registrar/', registrar_usuario_persona,
         name='registrar_usuario_persona'),
    path('login/', iniciar_sesion, name='iniciar_sesion'),
    path('agendar_cita/', agendar_cita, name='agendar_cita'),
    path('retrasar_cita/<int:cita_id>/',
         retrasar_cita, name='retrasar_cita'),
]
