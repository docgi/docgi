from rest_framework import viewsets, mixins

from docgi.base.apis import REGEX_UUID
from . import models, serializers, services, permissions


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.BoardSerializer
    queryset = models.Board.objects.all()
    permission_classes = (
        permissions.BoardPermission,
    )
    lookup_value_regex = REGEX_UUID

    def get_queryset(self):
        cur_user = self.request.user
        return services.get_user_board(
            user=cur_user,
            workspace=cur_user.current_workspace
        )


class BoarColumnViewSet(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = serializers.BoardColumnSerializer
    queryset = models.BoardColumn.objects.all()
    permission_classes = (permissions.BoardColumnPermission,)
    lookup_value_regex = REGEX_UUID


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TaskSerializer
    queryset = models.Task.objects.all()
    permission_classes = (
        permissions.TaskPermission
    )
    lookup_value_regex = REGEX_UUID
