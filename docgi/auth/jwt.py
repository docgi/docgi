from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import KEY_WORKSPACE_NAME_OBTAIN_TOKEN, KEY_WORKSPACE_ROLE_OBTAIN_TOKEN

KEY_USER_WORKSPACE_NAME = "workspace_name"
KEY_USER_WORKSPACE_ROLE = "workspace_role"


class DocgiJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        setattr(user, KEY_USER_WORKSPACE_NAME, validated_token.get(KEY_WORKSPACE_NAME_OBTAIN_TOKEN))
        setattr(user, KEY_USER_WORKSPACE_ROLE, validated_token.get(KEY_WORKSPACE_ROLE_OBTAIN_TOKEN))
        return user
