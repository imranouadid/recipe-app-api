from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user import serializers


# Create a new user in the system
class CreateUserView(generics.CreateAPIView):
    serializer_class = serializers.UserSerializer


# Create a new auth token for user
class CreateTokenView(ObtainAuthToken):
    serializer_class = serializers.AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
