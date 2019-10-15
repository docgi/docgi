from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from apps.utils import strings, mailer
from . import models, serializers


class CheckWorkspaceView(APIView):
    permission_classes = [
        AllowAny
    ]

    @swagger_auto_schema(
        request_body=serializers.CheckWorkspaceSerializer
    )
    def post(self, request, *args, **kwargs):
        serializer = serializers.CheckWorkspaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workspace = models.Workspace.objects.filter(
            name__iexact=serializer.data["name"]
        ).first()

        if workspace is None:
            return Response(data=dict(exist=False), status=status.HTTP_200_OK)

        data = {
            "exist": True,
            "name": workspace.name,
            "logo": request.build_absolute_uri(workspace.logo.url)
        }
        return Response(data=data, status=status.HTTP_200_OK)


class CreateWorkspaceApi(GenericViewSet):
    serializer_class = None

    @action(
        detail=False, methods=["post"],
        serializer_class=serializers.GetCodeSerializer,
        url_path="get-code"
    )
    def get_code(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data["email"]
        self._set_cache_and_email(email=email)

        return Response(status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["post"],
        serializer_class=serializers.CheckCodeSerializer,
        url_path="check-code"
    )
    def check_code(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        key_cache = self._get_key_cache(email=serializer.data["email"])
        cache_code = cache.get(key_cache)
        if cache_code is None or cache_code != serializer.data["code"]:
            raise ValidationError("Invalid code.")
        return Response(status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["post"],
        serializer_class=serializers.CreateWorkspaceSerializer,
        url_path="create"
    )
    def create_workspace(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        key_cache = self._get_key_cache(email=request.data["email"])
        code = cache.get(key_cache)
        if code != request.data["code"]:
            raise ValidationError("Invalid code.")
        serializer.save()
        cache.delete(key_cache)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _set_cache_and_email(self, email: str):
        code = strings.random_string_number(max_len=serializers.LEN_CODE)
        key = self._get_key_cache(email=email)
        cache.set(key, code)

        subject = "Welcome to docgi"
        ctx = dict(
            email=email,
            code=code
        )
        mailer.send_mail(subject=subject,
                         email=email,
                         text_template="email/getcode/email.txt",
                         html_template="email/getcode/email.html",
                         context=ctx)

    @classmethod
    def _get_key_cache(cls, email: str) -> str:
        key = f"{cls.__module__}#{cls.__class__}#{email}"
        return key
