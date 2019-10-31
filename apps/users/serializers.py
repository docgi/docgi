from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ("id", "email", "username", "avatar_thumbnail", "avatar")
        read_only_fields = ("avatar_thumbnail", "email")
        only_on_update_fields = ("username",)

    username = serializers.CharField(max_length=150, required=False)

    def validate_username(self, username):
        checker = models.User.objects.filter(
            username__iexact=username
        ).exclude(id=self.context["view"].kwargs.get("pk"))
        if checker.exists():
            raise serializers.ValidationError(f"{username} already used")
        return username

    def update(self, instance, validated_data: dict):
        avatar = validated_data.get("avatar", None)
        if avatar is not None:
            validated_data.update(avatar_thumbnail=avatar)
        return super().update(validated_data=validated_data, instance=instance)


class UserIdAndAvatarUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ("id", "avatar_thumbnail")
        read_only_fields = ("id", "avatar_thumbnail")
