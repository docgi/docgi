from django.core.validators import MinLengthValidator, MaxLengthValidator
from rest_framework import serializers

from . import models


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ("id", "avatar", "email", "username")
        read_only_fields = ("id", "avatar")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ("id", "email", "username", "avatar")
        read_only_fields = ("email",)
        only_on_update_fields = ("username",)
        extra_kwargs = {
            "username": {
                "required": False
            }
        }

    def validate_username(self, username):
        checker = models.User.objects.filter(
            username__iexact=username
        ).exclude(id=self.context["view"].kwargs.get("pk"))
        if checker.exists():
            raise serializers.ValidationError(f"{username} already used")
        return username


class ChangePasswordSerializer(serializers.Serializer):
    old_pass = serializers.CharField(max_length=150)
    new_pass = serializers.CharField(max_length=150, min_length=8)
    repeat_pass = serializers.CharField(max_length=150, min_length=8)

    def validate_old_pass(self, old_pass: str):
        user = self.context["request"].user
        if user.check_password(old_pass):
            return old_pass

        raise serializers.ValidationError("Wrong old password.")

    def validate(self, attrs):
        new_pass = attrs.get("new_pass")
        repeat_pass = attrs.get("repeat_pass")

        if new_pass != repeat_pass:
            raise serializers.ValidationError({
                "new_pass": "New pass and repeat pass doesn't match."
            })
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        new_pass = validated_data.pop("new_pass")
        user.set_password(raw_password=new_pass)
        user.save()
        return user


class UserSetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(validators=[
        MinLengthValidator(8), MaxLengthValidator(50)
    ])
    confirm_password = serializers.CharField(validators=[
        MinLengthValidator(8), MaxLengthValidator(50)
    ])

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Password and password confirm does not match."})
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        raw_password = validated_data.get("password")
        if user.has_usable_password():
            raise serializers.ValidationError({"error": "Password has been set before."})

        user.set_password(raw_password=raw_password)
        user.save()
        return user

    def to_representation(self, user: models.User):
        ret = dict(
            user=UserInfoSerializer(instance=user, context=self.context).data,
            workspace_name=user.get_current_workspace_name()
        )
        return ret
