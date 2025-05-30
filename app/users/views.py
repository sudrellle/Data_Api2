from django.shortcuts import render
from users.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    
)
from rest_framework import generics,authentication,permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
# Create your views here.

class CreateUserView(generics.CreateAPIView):
    serializer_class=UserSerializer


class CreateTokenView(ObtainAuthToken):
    serializer_class=AuthTokenSerializer
    renderer_classes=api_settings.DEFAULT_RENDERER_CLASSES

    

class ManageApiView(generics.RetrieveUpdateAPIView):
    serializer_class=UserSerializer
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)
    
    def get_object(self):
        return self.request.user
    
    

    



