from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import SlugField
from rest_framework_simplejwt.serializers import TokenObtainSerializer, RefreshToken

from docgi.workspaces.models import WorkspaceMember


KEY_WORKSPACE_NAME_OBTAIN_TOKEN = "workspace_name"
KEY_WORKSPACE_ROLE_OBTAIN_TOKEN = "workspace_role"


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
