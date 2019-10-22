from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from . import serializers


class DocgiTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = serializers.DocgiTokenObtainPairSerializer
