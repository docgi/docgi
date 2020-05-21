from django.contrib.auth import get_user_model
from rest_framework import serializers

from docgi.base.serializer_fields import ColorField
from docgi.base.serializers import (
    DocgiSerializerUtilMixin, DocgiFlexToPresentMixin, DocgiExtraReadOnlyField
)
from . import models
from ..users.serializers import UserInfoSerializer

User = get_user_model()


class SimpleCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = (
            "id", "name", "creator", "emoji", "color", "is_collection"
        )

    is_collection = serializers.BooleanField(read_only=True, default=True)


class SimpleDocsInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = (
            "id", "name", "is_doc", "created", "creator",
            "modified", "draft", "collection", "last_update_by"
        )
    creator = UserInfoSerializer(read_only=True)
    last_update_by = UserInfoSerializer(read_only=True)
    is_doc = serializers.BooleanField(read_only=True, default=True)


class CollectionSerializer(DocgiSerializerUtilMixin,
                           serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = (
            "id", "name", "workspace", "creator", "emoji",
            "private", "color", "children", "is_collection",
        )
        read_only_fields = ("workspace", "creator",)

    color = ColorField(required=False, default="f5f5f5")
    children = serializers.SerializerMethodField()
    is_collection = serializers.BooleanField(read_only=True, default=True)

    def validate_name(self, name):
        view = self.context["view"]
        checker = models.Collection.objects.filter(
            name__iexact=name,
            workspace_id=self.cur_user.get_current_workspace_id(),
        )
        if self.is_update_action():
            checker = checker.exclude(id=view.kwargs.get("pk"))

        if checker.exists():
            raise serializers.ValidationError("That name already taken.")

        return name

    def get_children(self, obj):
        child_docs = SimpleDocsInfoSerializer(
            instance=obj.documents.all(),
            many=True,
            context=self.context
        ).data
        return child_docs

    def create(self, validated_data: dict):
        user = self.context["request"].user
        workspace_id = self.context["request"].user.get_current_workspace_id()

        validated_data.update(
            creator=user,
            workspace_id=workspace_id
        )
        return super().create(validated_data=validated_data)


class DocumentSerializer(DocgiFlexToPresentMixin,
                         DocgiSerializerUtilMixin,
                         DocgiExtraReadOnlyField,
                         serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = (
            "id", "name", "html_content", "json_content", "star",
            "contributors", "creator", "collection", "is_docs",
            "created", "modified", "draft", "last_update_by"
        )
        read_only_fields = ("contributors", "creator")
        create_only_fields = ("collection",)
        flex_represent_fields = {
            "contributors": {
                "presenter": "docgi.users.serializers.UserInfoSerializer",
                "many": True
            },
        }

    star = serializers.IntegerField(read_only=True, default=0)
    is_docs = serializers.BooleanField(read_only=True, default=True)
    creator = UserInfoSerializer(read_only=True)
    last_update_by = UserInfoSerializer(read_only=True)

    def get_fields(self):
        fields = super().get_fields()
        if self.is_update_action():
            setattr(fields["name"], "required", False)
        return fields

    def validate_collection(self, collection):
        current_workspace = self.context["request"].user.get_current_workspace_id()
        if collection.workspace_id != current_workspace:
            raise serializers.ValidationError()
        return collection

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data.update(
            creator=user,
            last_update_by=user
        )
        return super().create(validated_data=validated_data)

    def update(self, instance, validated_data):
        current_user = self.context["request"].user
        validated_data.update(
            last_update_by=current_user
        )

        contributors = instance.contributors.all()
        instance = super().update(instance, validated_data)

        if current_user.id not in [user.id for user in contributors]:
            instance.contributors.add(current_user)

        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        # Ignore both fields on create action, because client already hold it
        if self.is_create_action():
            ret.pop("html_content")
            ret.pop("json_content")

        return ret


class DocumentImageSerializer(DocgiFlexToPresentMixin,
                              DocgiSerializerUtilMixin,
                              serializers.ModelSerializer):
    class Meta:
        model = models.DocumentImage
        fields = (
            "image",
        )

    def create(self, validated_data):
        validated_data.update(
            workspace_id=self.cur_user.get_current_workspace_id()
        )
        return super().create(validated_data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        url = ret.pop("image")
        ret["src"] = url
        return ret
