from django.db import transaction
from rest_framework import serializers

from docgi.base.serializers import DocgiSerializerUtilMixin
from . import models


_default_column_template = [
    {
        "name": "Todo"
    },
    {
        "name": "Doing"
    },
    {
        "name": "Done"
    }
]


def _get_board_column_template(board: models.Board, template=None):
    if template is None:
        template = _default_column_template

    for item in template:
        item.update(dict(
            board=board
        ))

    return template


class TaskSerializer(DocgiSerializerUtilMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = (
            "id", "name", "board_scope_id", "board", "board_column"
        )

    def create(self, validated_data):
        validated_data.update(
            creator=self.cur_user,
            board=models.Board.objects.first()
        )
        return super().create(validated_data)


class BoardColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BoardColumn
        fields = (
            "id", "board", "name"
        )


class BoardSerializer(DocgiSerializerUtilMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Board
        fields = (
            "id", "name", "tasks", "columns", "private"
        )

    tasks = TaskSerializer(many=True, read_only=True)
    columns = BoardColumnSerializer(many=True, read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        validated_data.update(
            creator=self.cur_user,
            workspace=self.cur_user.current_workspace
        )
        board = super().create(validated_data)

        # Include creator as member of board.
        models.BoardMembers.objects.create(
            board=board,
            user=self.cur_user
        )

        # Then we init three default columns for it.
        columns = [models.BoardColumn(**item) for item in _get_board_column_template(
            board=board, template=None
        )]
        models.BoardColumn.objects.bulk_create(columns)

        return board
