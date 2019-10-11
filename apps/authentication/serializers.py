from rest_framework.exceptions import AuthenticationFailed
from rest_framework.serializers import SlugField
from rest_framework_simplejwt.serializers import TokenObtainSerializer, RefreshToken

from apps.workspaces.models import WorkspaceMember


class DocgiTokenObtainPairSerializer(TokenObtainSerializer):
    workspace = SlugField(required=True)

    @classmethod
    def get_token(cls, user, **kwargs):
        token = RefreshToken.for_user(user)
        for k, v in kwargs.items():
            token[k] = v
        return token

    def validate(self, attrs):
        workspace = attrs.get("workspace")
        data = super().validate(attrs)

        workspace_member = WorkspaceMember.objects.filter(
            user_id=self.user.id, workspace__name__iexact=workspace
        ).first()
        if workspace_member is None:
            raise AuthenticationFailed()
        refresh = self.get_token(
            self.user,
            workspace=workspace_member.workspace_id,
            member_id=workspace_member.id
        )
        data["token"] = str(refresh.access_token)

        return data
