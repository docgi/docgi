from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics

from . import serializers


class DocgiTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = serializers.DocgiTokenObtainPairSerializer


class DocgiForgotPassword(generics.CreateAPIView):
    serializer_class = serializers.ForgotPasswordSerializer
    permission_classes = (AllowAny,)


class DocgiResetPassword(generics.CreateAPIView):
    serializer_class = serializers.ResetPasswordSerializer
    authentication_classes = ()
    permission_classes = ()
