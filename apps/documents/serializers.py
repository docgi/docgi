from typing import Sequence

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.utils.serializers import (
    DocgiModelSerializerMixin, UPDATE_ACTIONS,
    DocgiFlexToPresentSerializerMixin)
from apps.workspaces.models import WorkspaceMember
from . import models

User = get_user_model()


class CollectionMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id",)


class CollectionSerializer(DocgiFlexToPresentSerializerMixin, DocgiModelSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ("id", "name", "workspace", "creator", "members")
        read_only_fields = ("workspace", "creator")
        only_create_fields = ("members",)
        on_represent_fields_maps = {
            "members": {
                "class": CollectionMemberSerializer,
                "many": True
            }
        }

    members = serializers.ListField(
        child=serializers.IntegerField(),
        required=False, allow_empty=True, allow_null=False,
    )

    def validate_name(self, name):
        view = self.context["view"]
        request = self.context["request"]
        checker = models.Collection.objects.filter(
            name__iexact=name, workspace_id=request.user.workspace
        )
        if view.action in UPDATE_ACTIONS:
            checker = checker.exclude(id=view.kwargs.get("pk"))

        if checker.exists():
            raise serializers.ValidationError("That name already used.")

        return name

    def validate_members(self, members: Sequence[int]) -> Sequence[int]:
        workspace_id = self.context["request"].user.workspace
        return WorkspaceMember.validate_members(
            workspace_id=workspace_id,
            user_ids=members
        )

    def create(self, validated_data: dict):
        user = self.context["request"].user
        workspace_id = self.context["request"].user.workspace
        members = validated_data.pop("members", [])

        validated_data.update(
            creator=user,
            workspace_id=workspace_id
        )
        instance = super().create(validated_data=validated_data)

        # Include creator
        if user.id not in members:
            members.append(user.id)

        objs = list()
        CollectionMemberClass = models.Collection.members.through
        for user_id in members:
            objs.append(CollectionMemberClass(
                user_id=user_id, collection=instance
            ))
        CollectionMemberClass.objects.bulk_create(objs)

        return instance
