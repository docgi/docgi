from rest_framework import viewsets, mixins
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from . import models, serializers


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  GenericViewSet):
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()
    permission_classes = [AllowAny]

    def get_parsers(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return [MultiPartParser()]
        return super().get_parsers()
