from typing import Sequence

from django.contrib.auth import get_user_model
from dumas.serializers import FlexToPresentMixin, ExtraReadOnlyField
from rest_framework import serializers

from apps.users.serializers import UserInfoSerializer
from apps.utils.docgi_serializers import UPDATE_ACTIONS, ColorField
from apps.workspaces.models import WorkspaceMember
from . import models

User = get_user_model()


class CollectionSerializer(FlexToPresentMixin,
                           ExtraReadOnlyField,
                           serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ("id", "name", "workspace", "creator", "members", "private", "parent", "has_child", "color")
        read_only_fields = ("workspace", "creator")
        create_only_fields = ("members",)
        extra_kwargs = {
            "parent": {
                "write_only": True
            }
        }
        flex_represent_fields = {
            "members": {
                "presenter": UserInfoSerializer,
                "many": True
            }
        }

    members = serializers.ListField(
        child=serializers.IntegerField(),
        required=False, allow_empty=True, allow_null=False,
    )
    has_child = serializers.BooleanField(default=False, read_only=True)
    color = ColorField()

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

    def validate_parent(self, parent: models.Collection):
        request = self.context["request"]
        view = self.context["view"]
        current_workspace = request.user.workspace
        if parent.workspace_id != current_workspace:
            raise serializers.ValidationError("Invalid parent")

        if request.method in ["POST", "PATCH"]:
            if parent.id == view.kwargs.get("pk"):
                raise serializers.ValidationError("Invalid parent")

        return parent

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


class DocumentSerializer(FlexToPresentMixin,
                         ExtraReadOnlyField,
                         serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = ("id", "title", "contents", "star", "contributors", "creator", "collection")
        read_only_fields = ("contributors", "creator")
        create_only_fields = ("collection",)
        flex_represent_fields = {
            "contributors": {
                "presenter": "apps.users.serializers.UserInfoSerializer",
                "many": True
            }
        }

    star = serializers.IntegerField(read_only=True, default=0)

    def validate_collection(self, collection):
        current_workspace = self.context["request"].user.workspace
        if collection.workspace_id != current_workspace:
            raise serializers.ValidationError()
        return collection

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data.update(
            creator=user
        )
        return super().create(validated_data=validated_data)

    def update(self, instance, validated_data):
        current_user = self.context["request"].user
        contributors = instance.contributors.all()
        instance = super().update(instance, validated_data)

        if current_user.id != instance.creator_id and \
                current_user.id not in [user.id for user in contributors]:
            instance.contributors.add(current_user)

        return instance
