from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import SlugField, Serializer, EmailField, ValidationError, CharField
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainSerializer, RefreshToken

from docgi.utils.mailer import send_mail
from docgi.workspaces.models import WorkspaceMember

User = get_user_model()

KEY_WORKSPACE_NAME_OBTAIN_TOKEN = "workspace_name"
KEY_WORKSPACE_ROLE_OBTAIN_TOKEN = "workspace_role"
FRONTEND_URL_RESET_PASS = "auth/reset-password"


class DocgiTokenObtainPairSerializer(TokenObtainSerializer):
    workspace = SlugField(required=True)

    @classmethod
    def get_token(cls, user, **kwargs):
        token = RefreshToken.for_user(user)
        for k, v in kwargs.items():
            token[k] = v
        return token

    def validate(self, attrs):
        workspace = attrs.pop("workspace")
        data = super().validate(attrs)

        try:
            workspace_member = WorkspaceMember.objects.get(
                user_id=self.user.id,
                workspace__name__iexact=workspace
            )
        except WorkspaceMember.DoesNotExist:
            raise AuthenticationFailed()
        refresh = self.get_token(
            self.user,
            **{
                KEY_WORKSPACE_NAME_OBTAIN_TOKEN: workspace_member.workspace_id,
                KEY_WORKSPACE_ROLE_OBTAIN_TOKEN: workspace_member.role
            }
        )
        data["token"] = str(refresh.access_token)

        return data


class ForgotPasswordSerializer(Serializer):
    email = EmailField()
    workspace = SlugField()
    client_origin = CharField(allow_blank=False)

    def validate(self, attrs):
        email = attrs.get("email")
        workspace = attrs.get("workspace")

        checker = WorkspaceMember.objects.filter(
            workspace=workspace,
            user__email__exact=email
        )
        if not checker.exists():
            raise ValidationError({
                "email": "Workspace not exist or you are not member of this workspace"
            })

        return attrs

    def create(self, validated_data):
        email = validated_data.get("email")
        workspace = validated_data.get("workspace")
        client_origin = validated_data.get("client_origin")

        user = User.objects.get(email__exact=email)
        reset_token = DocgiTokenObtainPairSerializer.get_token(
            user=user,
            is_reset=True,
            **{KEY_WORKSPACE_NAME_OBTAIN_TOKEN: workspace}
        )
        reset_link = urljoin(client_origin, f"{FRONTEND_URL_RESET_PASS}?token={reset_token}")

        context = dict(
            email=email,
            reset_link=reset_link,
            workspace=workspace
        )

        return send_mail(
            subject="Forgot password",
            email=email,
            text_template_path="email/forgot_password/forgot_password.txt",
            html_template_path="email/forgot_password/forgot_password.html",
            context=context
        )

    def to_representation(self, status):
        return {
            "send": status
        }


class ResetPasswordSerializer(Serializer):
    password = CharField(validators=[
        MinLengthValidator(8), MaxLengthValidator(50)
    ])
    confirm_password = CharField(validators=[
        MinLengthValidator(8), MaxLengthValidator(50)
    ])
    token = CharField()

    def validate(self, attrs):
        try:
            refresh_token = RefreshToken(attrs['token'])
            if not refresh_token.get("is_reset", False):
                raise ValidationError({
                    "token": ["Invalid token"]
                })
            attrs.update(refresh_token=refresh_token)
        except TokenError:
            raise ValidationError({
                "token": ["Expired token"]
            })

        if attrs["password"] != attrs["confirm_password"]:
            raise ValidationError({"confirm_password": "Password and password confirm does not match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.get(pk=validated_data["refresh_token"]["user_id"])
        raw_password = validated_data.get("password")
        user.set_password(raw_password=raw_password)
        user.save()
        return user

    def to_representation(self, user: User):
        return {
            "status": user.has_usable_password()
        }
