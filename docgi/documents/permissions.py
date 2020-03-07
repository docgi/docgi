from rest_framework.permissions import BasePermission

from . import models


class CollectionPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj: models.Collection):
        return obj.creator_id == request.user.id
