from rest_framework import serializers

from apps.utils.serializers import DocgiModelSerializerMixin, UPDATE_ACTIONS
from . import models


class CollectionSerializer(DocgiModelSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ("id", "name", "workspace", "creator", "members")
        read_only_fields = ("workspace", "creator")
        only_create_fields = ("members",)

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

    def create(self, validated_data: dict):
        user = self.context["request"].user
        workspace_id = self.context["request"].user.workspace

        validated_data.update(
            creator=user,
            workspace_id=workspace_id
        )
        return super().create(validated_data=validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        self.fields.pop("members", None)
        return super().to_representation(instance)
