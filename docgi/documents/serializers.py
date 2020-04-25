from django.contrib.auth import get_user_model
from dumas.serializers import FlexToPresentMixin, ExtraReadOnlyField
from rest_framework import serializers

from docgi.base.serializers import UPDATE_ACTIONS, ColorField
from . import models

User = get_user_model()


class CollectionSerializer(ExtraReadOnlyField,
                           serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = (
            "id", "name", "workspace", "creator",
            "private", "parent", "color", "child_cols", "docs"
        )
        read_only_fields = ("workspace", "creator")
        extra_kwargs = {
            "parent": {
                "write_only": True
            }
        }

    color = ColorField()
    docs = serializers.JSONField(read_only=True, default=list)
    child_cols = serializers.JSONField(read_only=True, default=list)

    def validate_name(self, name):
        view = self.context["view"]
        request = self.context["request"]
        checker = models.Collection.objects.filter(
            name__iexact=name, workspace_id=request.user.get_current_workspace_id()
        )
        if view.action in UPDATE_ACTIONS:
            checker = checker.exclude(id=view.kwargs.get("pk"))

        if checker.exists():
            raise serializers.ValidationError("That name already used.")

        return name

    def validate_parent(self, parent: models.Collection):
        request = self.context["request"]
        view = self.context["view"]
        current_workspace = request.user.get_current_workspace_id()
        if parent.workspace_id != current_workspace:
            raise serializers.ValidationError("Invalid parent")

        if request.method in ["PUT", "PATCH"]:
            if parent.id == view.kwargs.get("pk"):
                raise serializers.ValidationError("Invalid parent")

        return parent

    def create(self, validated_data: dict):
        user = self.context["request"].user
        workspace_id = self.context["request"].user.get_current_workspace_id()

        validated_data.update(
            creator=user,
            workspace_id=workspace_id
        )
        return super().create(validated_data=validated_data)


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
                "presenter": "docgi.users.serializers.UserInfoSerializer",
                "many": True
            }
        }

    star = serializers.IntegerField(read_only=True, default=0)

    def validate_collection(self, collection):
        current_workspace = self.context["request"].user.get_current_workspace_id()
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
