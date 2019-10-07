from rest_framework import serializers

from apps.users.models import User
from . import models

MAX_LEN_CODE = 6


class CheckWorkspaceSerializer(serializers.Serializer):
    name = serializers.SlugField(required=True)


class GetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CheckCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=MAX_LEN_CODE)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class CreateWorkspaceSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, max_length=MAX_LEN_CODE)
    workspace_name = serializers.SlugField(required=True)

    def validate_workspace_name(self, workspace_name: str) -> str:
        if models.Workspace.objects.filter(name__iexact=workspace_name).exists():
            raise serializers.ValidationError(f"Workspace name {workspace_name} already exits.")
        return workspace_name

    def create(self, validated_data):
        user = User.get_or_create(email=validated_data["email"])
        workspace = models.Workspace.objects.create(
            name=validated_data["workspace"]
        )
        models.WorkspaceMember.objects.create(
            user=user,
            workspace=workspace
        )
        return User  # TODO: return jwt

class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Workspace
        fields = "__all__"
