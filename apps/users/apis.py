from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny

from . import models, serializers


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()
    permission_classes = [AllowAny]

    def get_parsers(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return [MultiPartParser()]
        return super().get_parsers()
