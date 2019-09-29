from django.conf import settings as app_settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import EmailValidator
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from apps.utils import strings
from . import models, serializers


class CheckWorkspaceView(APIView):
    permission_classes = [
        AllowAny
    ]

    def post(self, request, *args, **kwargs):
        """
        Check workspace exists or not with `name`
        """
        workspace_name = request.data.get("name", None)
        if workspace_name is None:
            return Response(
                data=dict(error="Invalid payload."),
                status=status.HTTP_400_BAD_REQUEST
            )

        is_exists = models.Workspace.objects.filter(
            name__iexact=workspace_name
        ).exists()
        return Response(
            data=dict(exists=is_exists),
            status=status.HTTP_200_OK
        )


class CreateWorkspaceApi(GenericViewSet):
    serializer_class = None

    @action(
        detail=False, methods=["post"],
        serializer_class=serializers.GetCodeSerializer,
        url_path="get-code"
    )
    def get_code(self, request):
        email = request.data.get("email", None)
        if email is None:
            return Response(
                data=dict(error="Email is required."),
                status=status.HTTP_400_BAD_REQUEST
            )

        validator = EmailValidator()
        try:
            validator(email)
        except ValidationError as ex:
            return Response(
                data=dict(error=ex.message),
                status=status.HTTP_400_BAD_REQUEST
            )

        code = strings.random_string_number(max_len=6)
        self._set_cache_and_email(email=email, code=code)

        return Response(status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["post"],
        serializer_class=serializers.CheckCodeSerializer,
        url_path="check-code"
    )
    def check_code(self, request):
        pass

    def _set_cache_and_email(self, email: str, code: str):
        ctx = dict(
            email=email,
            code=code
        )
        subject = "Welcome"
        text_content = render_to_string("email/getcode/getcode.txt", ctx)
        html_content = render_to_string("email/getcode/getcode.html", ctx)
        msg = EmailMultiAlternatives(subject, text_content, app_settings.ADMIN_EMAIL, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        cache.set(email, code)
