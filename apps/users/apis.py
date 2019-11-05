from django.db import transaction
from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from . import serializers


class UserMeApi(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user

    def get_parsers(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [MultiPartParser()]
        return super().get_parsers()


class UserChangePasswordApi(generics.CreateAPIView):
    serializer_class = serializers.ChangePasswordSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(status=status.HTTP_200_OK)
