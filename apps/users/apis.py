from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, serializers


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()
    permission_classes = [AllowAny]

    def get_parsers(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return [MultiPartParser()]
        return super().get_parsers()


class GetEmailCodeAPIView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email", None)
        if email is None:
            raise Response(
                data=dict(error="Email is required."),
                status=status.HTTP_400_BAD_REQUEST
            )
