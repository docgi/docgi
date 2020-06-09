from django.contrib.auth import get_user_model

from docgi.workspaces.models import Workspace
from . import models

User = get_user_model()


def get_user_board(user: User, workspace: "Workspace", queryset=models.Board.objects.all()):
    return queryset.filter(
        workspace=workspace
    )


def get_user_task(user: User, workspace: Workspace, queryset=models.Task.objects.all()):
    return queryset.filter(
        workspace=workspace
    )
