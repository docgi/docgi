from typing import Sequence

from django.contrib.auth import get_user_model
from rest_framework import serializers
from dumas.serializers import FlexToPresentMixin, ExtraReadOnlyField

from apps.users.serializers import UserInfoSerializer
from apps.utils.serializers import UPDATE_ACTIONS
from apps.workspaces.models import WorkspaceMember
from . import models

User = get_user_model()


class CollectionSerializer(FlexToPresentMixin,
                           ExtraReadOnlyField,
                           serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ("id", "name", "workspace", "creator", "members")
        read_only_fields = ("workspace", "creator")
        only_create_fields = ("members",)
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


class ListDocumentSerializer(FlexToPresentMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = ("id", "title", "star", "creator", "collection")
        flex_represent_fields = {
            "contributors": {
                "class": UserInfoSerializer,
                "many": True,
            },
            "creator": {
                "class": UserInfoSerializer
            }
        }

    star = serializers.IntegerField(read_only=True, default=0)


class DocumentSerializer(FlexToPresentMixin,
                         ExtraReadOnlyField,
                         serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = ("id", "title", "contents", "star", "contributors", "creator", "collection")
        read_only_fields = ("contributors",)
        only_create_fields = ("collection",)
        flex_represent_fields = {
            "contributors": {
                "class": "docgi.apps.users.serializers.UserInfoSerializer",
                "many": True
            },
            "creator": {
                "class": UserInfoSerializer
            }
        }

    star = serializers.IntegerField(read_only=True, default=0)
    contributors = serializers.ListField(
        child=UserInfoSerializer(), read_only=True
    )

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
