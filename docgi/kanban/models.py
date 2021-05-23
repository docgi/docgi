import uuid as uuid

from django.contrib.auth import get_user_model
from django.db.models import JSONField
from django.db import models
from django.db.models import UniqueConstraint
from model_utils.models import TimeStampedModel

User = get_user_model()
UNIQUE_TASK_BOARD_SCOPE_ID = "task_unique_board_scope_id"


class Board(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    short_desc = JSONField(default=list, blank=True)

    name = models.TextField()
    private = models.BooleanField(default=False)

    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="boards"
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="+"
    )

    class Meta:
        ordering = ("created",)

    def is_public(self):
        return self.private is False

    def is_private(self):
        return self.private is True

    def __str__(self):
        return self.name


class BoardMembers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="members")

    class Meta:
        unique_together = ("user", "board")

    def __str__(self):
        return f"User {self.user_id} of Board {self.board_id}"


class BoardColumn(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.TextField()

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="columns"
    )

    def __str__(self):
        return self.name


class Task(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board_scope_id = models.PositiveIntegerField(editable=False)

    name = models.TextField()

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    board_column = models.ForeignKey(
        BoardColumn,
        on_delete=models.SET_NULL,
        null=True,
        related_name="+"
    )

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="+"
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            UniqueConstraint(fields=["board", "board_scope_id"], name=UNIQUE_TASK_BOARD_SCOPE_ID)
        ]

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # If insert we count total tasks of board belong to and set for `board_scope_id` of current `task`
        if force_insert:
            current_number_task_of_board = Task.objects.filter(
                board_id=self.board_id
            ).count()
            if current_number_task_of_board == 0 or current_number_task_of_board is None:
                board_scope_id = 1  # first task of board
            else:
                board_scope_id = current_number_task_of_board + 1
            self.board_scope_id = board_scope_id

        super().save(force_insert=force_insert, force_update=force_update,
                     using=using, update_fields=update_fields)
