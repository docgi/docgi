from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.authentication.serializers import DocgiTokenObtainPairSerializer
from . import models

User = get_user_model()
MAX_LEN_CODE = 6


class CheckWorkspaceSerializer(serializers.Serializer):
    name = serializers.SlugField(required=True)


class GetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class CheckCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=MAX_LEN_CODE)


class CreateWorkspaceSerializer(serializers.Serializer):
    class InnerUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ("id", "email", "username", "avatar_thumbnail")

    email = serializers.EmailField(required=True, write_only=True)
    code = serializers.CharField(required=True, max_length=MAX_LEN_CODE, write_only=True)
    workspace_name = serializers.SlugField(required=True, write_only=True)

    def validate_workspace_name(self, workspace_name: str) -> str:
        if models.Workspace.objects.filter(name__iexact=workspace_name).exists():
            raise serializers.ValidationError("Workspace with that name already exists.")
        return workspace_name

    def create(self, validated_data):
        user = User.get_or_create(email=validated_data["email"])
        workspace = models.Workspace.objects.create(
            name=validated_data["workspace_name"]
        )
        models.WorkspaceMember.objects.create(
            user=user,
            workspace=workspace
        )
        return dict(
            user=user,
            workspace=workspace
        )

    def to_representation(self, data):
        user = data["user"]
        workspace = data["workspace"]
        ret = dict()
        ret["user"] = self.InnerUserSerializer(instance=user, context=self.context).data
        ret["token"] = str(DocgiTokenObtainPairSerializer.get_token(
            user=user, workspace=workspace.name
        ).access_token)
        return ret
