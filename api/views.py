import os
import base64
import requests
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, AllowAny
from api.serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint: Permite ver o editar a los usuarios.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class CustomAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class ImagesViewset(viewsets.ViewSet):
    """
   API endpoint: Permite listar o subir imagenes a una api interna.
   """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            final_endpoint = settings.API_IMAGENES
            response = requests.get(final_endpoint, headers={
                'user': 'User123',
                'password': 'Password123'
            })

            if not response.status_code in [200, 201, 202]:
                return Response({'detail': f'Error en la api interno: {str(response.reason)}'},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({'data': response.json()}, status=status.HTTP_200_OK)
        except Exception as e:
            print('ERROR: ', str(e))
            return Response({'detail': 'No fue posible obtener el listado de imagenes'},
                            status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        try:
            data = request.data
            final_endpoint = settings.API_IMAGENES

            #   Nombre requerido
            file_name = data.get('file_name', None)
            if file_name is None:
                return Response({'detail': 'El nombre de la imagen es requerido'},
                                status=status.HTTP_400_BAD_REQUEST)

            #   VALIDACION DE IMAGEN
            file = data.get('file', None)
            if file is None:
                return Response({'detail': 'La imagen es requerida'},
                                status=status.HTTP_400_BAD_REQUEST)
            extension = os.path.splitext(file.name)[1].lower()

            if not extension.lower() in ['.jpg', '.png', '.jpeg', '.gif']:
                return Response({'detail': 'El archivo no es una imagen'},
                                status=status.HTTP_400_BAD_REQUEST)

            #   CONVERTIR IMAGEN A BASE64
            encoded_string = base64.b64encode(file.read()).decode('utf-8')

            body = {
                "imagene": {
                    "nombre": file_name,
                    "base64": encoded_string
                }
            }

            response = requests.post(final_endpoint, body, headers={
                'user': 'User123',
                'password': 'Password123'
            })

            if not response.status_code in [200, 201, 202]:
                return Response({'detail': f'Error en la api interno: {str(response.reason)}'},
                                status=status.HTTP_400_BAD_REQUEST)

            return Response({}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print('ERROR: ', str(e))
            return Response({'detail': 'No fue posible subir la imagen, intenta mas tarde'},
                            status=status.HTTP_400_BAD_REQUEST)
