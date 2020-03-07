from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import SlugField
from rest_framework_simplejwt.serializers import TokenObtainSerializer, RefreshToken

from docgi.workspaces.models import WorkspaceMember


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
                user_id=self.user.id, workspace__name__iexact=workspace
            )
        except WorkspaceMember.DoesNotExist:
            raise AuthenticationFailed()
        refresh = self.get_token(
            self.user,
            workspace=workspace_member.workspace_id,
            member_id=workspace_member.id,
            workspace_role=workspace_member.role,
        )
        data["token"] = str(refresh.access_token)

        return data
