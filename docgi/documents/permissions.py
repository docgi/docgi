from rest_framework.permissions import BasePermission

from . import models
from ..base.permissions import DocgiPermissionHelper


class CollectionPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj: models.Collection):
        if DocgiPermissionHelper.is_workspace_admin(request):
            return True

        if request.method == "DELETE":
            return obj.creator_id == request.user.id

        return request.user.is_authenticated
