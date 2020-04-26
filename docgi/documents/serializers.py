from django.contrib.auth import get_user_model
from rest_framework import serializers

from docgi.base.serializer_fields import UPDATE_ACTIONS, ColorField
from docgi.base.serializers import (
    DocgiSerializerUtilMixin, DocgiFlexToPresentMixin, DocgiExtraReadOnlyField
)
from . import models

User = get_user_model()


class SimpleCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = (
            "id", "name", "creator", "emoji", "color", "is_collection", "uuid"
        )

    is_collection = serializers.BooleanField(read_only=True, default=True)


class SimpleDocsInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = (
            "id", "name", "is_doc", "uuid"
        )

    name = serializers.CharField(read_only=True, source="title")
    is_doc = serializers.BooleanField(read_only=True, default=True)


class CollectionSerializer(DocgiFlexToPresentMixin,
                           DocgiSerializerUtilMixin,
                           serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = (
            "id", "name", "workspace", "creator", "emoji", "parent",
            "private", "parent", "color", "children", "is_collection", "uuid"
        )
        read_only_fields = ("workspace", "creator",)

    color = ColorField(required=False, default="ffffff")
    children = serializers.SerializerMethodField()
    is_collection = serializers.BooleanField(read_only=True, default=True)

    def validate_name(self, name):
        view = self.context["view"]
        request = self.context["request"]

        parent_id = self.initial_data.get("parent", None)
        if self.context["view"].action in ("update", "partial_update"):
            parent_id = parent_id or self.instance.parent_id

        checker = models.Collection.objects.filter(
            name__iexact=name,
            workspace_id=request.user.get_current_workspace_id(),
            parent_id=parent_id
        )
        if view.action in UPDATE_ACTIONS:
            checker = checker.exclude(id=view.kwargs.get("pk"))

        if checker.exists():
            raise serializers.ValidationError("That name already taken.")

        return name

    def validate_parent(self, parent: models.Collection):
        if parent is None:
            return None

        request = self.context["request"]
        view = self.context["view"]
        current_workspace = request.user.get_current_workspace_id()
        if parent.workspace_id != current_workspace:
            raise serializers.ValidationError("Invalid parent")

        if request.method in ["PUT", "PATCH"]:
            if parent.id == view.kwargs.get("pk"):
                raise serializers.ValidationError("Invalid parent")

        return parent

    def get_children(self, obj):
        child_cols = SimpleCollectionSerializer(
            instance=obj.children.all(),
            many=True,
            context=self.context
        ).data
        child_docs = SimpleDocsInfoSerializer(
            instance=obj.documents.all(),
            many=True,
            context=self.context
        ).data
        return child_docs + child_cols

    def create(self, validated_data: dict):
        user = self.context["request"].user
        workspace_id = self.context["request"].user.get_current_workspace_id()

        validated_data.update(
            creator=user,
            workspace_id=workspace_id
        )
        return super().create(validated_data=validated_data)


class DocumentSerializer(DocgiFlexToPresentMixin,
                         DocgiExtraReadOnlyField,
                         serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = (
            "id", "title", "contents", "star", "contributors",
            "creator", "collection", "is_docs", "uuid"
        )
        read_only_fields = ("contributors", "creator")
        create_only_fields = ("collection",)
        flex_represent_fields = {
            "contributors": {
                "presenter": "docgi.users.serializers.UserInfoSerializer",
                "many": True
            }
        }

    star = serializers.IntegerField(read_only=True, default=0)
    is_docs = serializers.BooleanField(read_only=True, default=True)

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
