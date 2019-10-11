from rest_framework_simplejwt.views import TokenObtainPairView

from . import serializers


class DocgiTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.DocgiTokenObtainPairSerializer
