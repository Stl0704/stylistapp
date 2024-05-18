from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, status
from .serializer import UsurarioInicio, PersonaInicio, LoginSerializer,UsuarioPersonaSerializer
from .models import Usuario, Persona, PersonaUsuario
from django.contrib.auth import authenticate



class UsuarioView(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    # Persona.objects.all()
    serializer_class = UsurarioInicio


class PersonaInicio(viewsets.ModelViewSet):
    queryset = Persona.objects.all()
    serializer_class = PersonaInicio


# FUNCION CREAR USUARIO - PERSONA

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




@api_view(['POST'])
def iniciar_sesion(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user_name = serializer.validated_data['user_name']
        password = serializer.validated_data['password']

        user = authenticate(username=user_name, password=password)
        
        if user is not None:
            return Response({'message': 'Inicio de sesión exitoso'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    

    
