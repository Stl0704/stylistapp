from django.urls import path , include
from rest_framework import routers
from . import views
from .views import registrar_usuario_persona,iniciar_sesion

router = routers.DefaultRouter()
router.register(r'Usuario',views.UsuarioView)
router.register(r'Persona',views.PersonaInicio)


urlpatterns = [
    path('',include (router.urls)),
    path('registrar/', registrar_usuario_persona, name='registrar_usuario_persona'),
    path('login/', iniciar_sesion, name='iniciar_sesion'),
]
