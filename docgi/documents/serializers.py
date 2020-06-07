from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from docgi.base.serializer_fields import ColorField
from docgi.base.serializers import (
    DocgiSerializerUtilMixin, DocgiFlexToPresentMixin, DocgiExtraReadOnlyField
)
from docgi.workspaces.serializers import WorkspacePublicInfoSerializer
from . import models, services
from ..users.serializers import UserInfoSerializer

User = get_user_model()


class SimpleDocsInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = (
            "id", "name", "created", "creator",
            "modified", "draft", "collection", "last_update_by",
        )

    creator = UserInfoSerializer(read_only=True)
    last_update_by = UserInfoSerializer(read_only=True)


class CollectionSerializer(DocgiSerializerUtilMixin,
                           DocgiExtraReadOnlyField,
                           serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = (
            "id", "name", "workspace", "creator", "emoji",
            "private", "color", "is_collection",
            "public", "public_by", "public_link"
        )
        read_only_fields = ("workspace", "creator", "public_by")
        extra_kwargs = {
            "public": {
                "required": False
            },
            "public_by": {
                "required": False
            },
            "name": {
                "required": False
            }
        }
        update_only_fields = ("public",)

    color = ColorField(required=False, default="f5f5f5")
    is_collection = serializers.SerializerMethodField()
    public_link = serializers.SerializerMethodField()

    def validate_name(self, name):
        view = self.context["view"]
        checker = models.Collection.objects.filter(
            name__iexact=name,
            workspace_id=self.cur_user.get_current_workspace_id(),
        )
        if self.is_update_method():
            checker = checker.exclude(id=view.kwargs.get("pk"))

        if checker.exists():
            raise serializers.ValidationError("That name already taken.")

        return name

    def get_public_link(self, collection):
        return services.build_public_collection_url(collection, self.get_request())

    def get_is_collection(self, _):
        return True

    def _validate_public(self, validated_data):
        public = validated_data.get("public", False)
        if public is True:
            validated_data.update(
                public_by=self.cur_user
            )
        else:
            validated_data.update(
                public_by=None
            )
        return validated_data

    def create(self, validated_data: dict):
        user = self.context["request"].user
        workspace_id = self.context["request"].user.get_current_workspace_id()

        validated_data = self._validate_public(validated_data)
        validated_data.update(
            creator=user,
            workspace_id=workspace_id
        )
        return super().create(validated_data=validated_data)

    def update(self, instance, validated_data):
        validated_data = self._validate_public(validated_data)
        return super().update(instance, validated_data)


class DocumentSerializer(DocgiFlexToPresentMixin,
                         DocgiSerializerUtilMixin,
                         DocgiExtraReadOnlyField,
                         serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = (
            "id", "name", "html_content", "json_content", "star",
            "contributors", "creator", "collection",
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
    creator = UserInfoSerializer(read_only=True)
    last_update_by = UserInfoSerializer(read_only=True)

    def get_fields(self):
        fields = super().get_fields()
        if self.is_update_method():
            setattr(fields["name"], "required", False)
        return fields

    def validate_collection(self, collection):
        current_workspace = self.context["request"].user.get_current_workspace_id()
        if collection.workspace_id != current_workspace:
            raise serializers.ValidationError()
        return collection

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        validated_data.update(
            creator=user,
            last_update_by=user
        )
        instance = super().create(validated_data=validated_data)
        instance.contributors.add(user)

        return instance

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
        if self.is_post_method():
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


class PublicDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = (
            "id", "name", "created", "modified", "collection", "html_content", "creator", "last_update_by"
        )

    creator = UserInfoSerializer(read_only=True)
    last_update_by = UserInfoSerializer(read_only=True)


class PublicCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = (
            "id", "name", "workspace", "creator", "emoji",
            "color", "children", "public",
        )
        read_only_fields = ("workspace", "creator", "public_by")

    color = ColorField(read_only=True)
    children = PublicDocSerializer(many=True, read_only=True, source="documents")
    workspace = WorkspacePublicInfoSerializer(read_only=True)
