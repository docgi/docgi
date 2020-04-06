from django.conf import settings as app_settings
from django.contrib.postgres.fields import JSONField
from django.core.cache import cache
from django.db.models import Subquery, OuterRef
from django.db.models.expressions import RawSQL
from django.core.exceptions import ValidationError as FieldValidationError
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, parsers
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from docgi.utils import strings, mailer
from . import models, serializers, permissions

HOST_NAME = app_settings.HOST_NAME


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

        result = dict(exist=False, workspace=None)
        if workspace is not None:
            workspace_data = serializers.WorkspacePublicInfoSerializer(instance=workspace,
                                                                       context={"request": self.request}).data
            result.update(exist=True, workspace=workspace_data)
        return Response(data=result, status=status.HTTP_200_OK)


class StatsWorkspaceAPI(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=serializers.StatsWorkspaceSerializer
    )
    def post(self, request, *args, **kwargs):
        serializer = serializers.GetCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_email = serializer.validated_data.get("email")
        workspaces = models.Workspace.objects.filter(
            name__in=Subquery(
                models.WorkspaceMember.objects.filter(
                    user__email__exact=user_email
                ).values_list("workspace")
            )
        )
        res = serializers.WorkspacePublicInfoSerializer(
            instance=workspaces, many=True, context={"view": self, "request": request}
        ).data

        return Response(res)


class CreateWorkspaceApi(GenericViewSet):
    serializer_class = None
    permission_classes = [
        AllowAny
    ]

    @action(
        detail=False, methods=["post"],
        serializer_class=serializers.GetCodeSerializer,
        url_path="get-code",
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
            raise ValidationError({"code": ["Invalid code"]})
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

        subject = f"Welcome to {HOST_NAME}"
        ctx = dict(
            email=email,
            code=code
        )
        mailer.send_mail(subject=subject,
                         email=email,
                         text_template_path="email/getcode/email.txt",
                         html_template_path="email/getcode/email.html",
                         context=ctx)

    @classmethod
    def _get_key_cache(cls, email: str) -> str:
        key = f"{cls.__module__}#{cls.__class__}#{email}"
        return key


class WorkspaceApi(RetrieveUpdateAPIView):
    serializer_class = serializers.WorkspaceSerializer
    parser_classes = [parsers.MultiPartParser]
    permission_classes = [
        (permissions.Read & permissions.IsMemberWorkspace) |
        (permissions.Update & permissions.IsAdminWorkspace)
    ]

    def get_object(self):
        return models.Workspace.objects.filter(
            name=self.request.user.current_workspace.name
        ).annotate(
            workspace_members=Subquery(
                models.WorkspaceMember.objects.filter(
                    workspace_id=OuterRef("pk")
                ).annotate(
                    members=RawSQL(
                        """
                        json_agg(
                            json_build_object(
                                'user', user_id::int,
                                'role', role::int
                            )
                        )
                        """
                        , ())
                ).values("members"),
                output_field=JSONField()
            )
        ).first()


class WorkspaceMemberAPI(ListModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = models.WorkspaceMember.objects.select_related("user").all()
    permission_classes = [
        (permissions.Read & permissions.IsMemberWorkspace) |
        (permissions.Update & permissions.IsAdminWorkspace)
    ]
    serializer_class = serializers.WorkspaceMemberSerializer
    lookup_field = "user"
    lookup_value_regex = r"\d+"

    def get_queryset(self):
        return self.queryset.filter(
            workspace_id__exact=self.request.user.get_current_workspace_name()
        )


class SendInvitationApi(CreateAPIView):
    serializer_class = serializers.SendInvitationSerializer
    permission_classes = (permissions.IsAdminWorkspace,)


class JoinInvitationApi(CreateAPIView):
    serializer_class = serializers.JoinInvitationSerializer
    permission_classes = (AllowAny,)


class CheckInvitationApi(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=serializers.JoinInvitationSerializer
    )
    def post(self, request, **kwargs):
        workspace = request.data.get("workspace")
        uuid = request.data.get("uuid")

        try:
            checker = models.Invitation.objects.filter(
                workspace_id=workspace,
                uuid=uuid
            )
            if not checker.exists():
                return Response(status=status.HTTP_404_NOT_FOUND)
        except FieldValidationError:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_200_OK)
