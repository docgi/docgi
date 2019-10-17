from rest_framework_simplejwt.authentication import JWTAuthentication


class DocgiJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        setattr(user, "workspace", validated_token.get("workspace"))
        setattr(user, "workspace_role", validated_token.get("workspace_role"))
        return user
