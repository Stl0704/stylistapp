from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets , status
from .serializer import UsurarioInicio , PersonaInicio , UsuarioPersonaSerializer
from .models import Usuario , Persona, PersonaUsuario


class UsuarioView(viewsets.ModelViewSet):
    queryset=Usuario.objects.all()
    #Persona.objects.all()
    serializer_class=UsurarioInicio
    

class PersonaInicio(viewsets.ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonaInicio
    
    
#FUNCION CREAR USUARIO - PERSONA

@api_view(['POST'])
def registrar_usuario_persona(request):
    if request.method == 'POST':
        serializer = UsuarioPersonaSerializer(data=request.data)
        if serializer.is_valid():
            usuario, persona, persona_usuario = serializer.save()
            return Response({
                'usuario_id': usuario.user_id,
                'persona_id': persona.persona_id,
                'persona_user_id': persona_usuario.persona_user_id
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
