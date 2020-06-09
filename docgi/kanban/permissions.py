from rest_framework.permissions import BasePermission

from docgi.base.permissions import DocgiPermissionHelper
from . import models


class BoardPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, board: models.Board):
        if DocgiPermissionHelper.is_delete(request):
            return request.user.id == board.creator_id

        if board.is_public():
            return True

        return models.BoardMembers.objects.filter(
            board=board,
            user=request.user,
            board__workspace=request.user.current_workspace
        ).exists()


class BoardColumnPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, col: models.BoardColumn):
        board = col.board

        if board.is_public():
            return True

        return models.BoardMembers.objects.filter(
            board=board,
            user=request.user,
            board__workspace=request.user.current_workspace
        ).exists()


class TaskPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, task: models.Task):
        board = task.board

        if board.is_public():
            return True

        return models.BoardMembers.objects.filter(
            board=board,
            user=request.user,
            board__workspace=request.user.current_workspace
        ).exists()
