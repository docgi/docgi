from rest_framework.permissions import BasePermission

from .models import WorkspaceMember

GET = "GET"
POST = "POST"
PUT = "PUT"
PATCH = "PATCH"
DELETE = "DELETE"


class Create(BasePermission):
    def has_permission(self, request, view):
        return request.method == POST


class Read(BasePermission):
    def has_permission(self, request, view):
        return request.method == GET


class Update(BasePermission):
    def has_permission(self, request, view):
        return request.method in [PATCH, PUT]


class Delete(BasePermission):
    def has_permission(self, request, view):
        return request.method == DELETE


class IsAdminWorkspace(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            return user.get_jwt_current_workspace_role() == WorkspaceMember.MemberRole.ADMIN.value
        return False


class IsMemberWorkspace(BasePermission):
    def has_permission(self, request, view):
        # Semantic purpose:
        #   Return `user.is_authenticated` because at DocgiTokenObtainPairSerializer
        #   in def `validate` we have check user is WorkspaceMember.
        return request.user.is_authenticated
