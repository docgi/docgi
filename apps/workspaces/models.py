from os import path
from typing import Sequence

from django.conf import settings as app_settings
from django.core.files.storage import get_storage_class
from django.db import models
from django.db.models import UniqueConstraint, Q

from model_utils.models import TimeStampedModel, SoftDeletableModel
from rest_framework.exceptions import ValidationError

storage = get_storage_class()()
UNIQUE_WORKSPACE_AND_USER_CONSTRAINT_NAME = "unique_workspace_user_constraint"


class Workspace(SoftDeletableModel, TimeStampedModel):
    def logo_path(self, filename, *args, **kwargs):
        paths = [
            app_settings.WORKSPACE_LOGO_DIR_NAME,
            str(self.name),
            path.basename(filename)
        ]
        return path.join(*paths)

    name = models.SlugField(unique=True,
                            primary_key=True,
                            max_length=128,
                            db_index=True)
    logo = models.FileField(storage=storage,
                            upload_to=logo_path,
                            null=True,
                            blank=True)

    def __str__(self):
        return self.name


class WorkspaceMember(SoftDeletableModel, TimeStampedModel):
    workspace = models.ForeignKey(Workspace,
                                  on_delete=models.CASCADE,
                                  related_name="members")
    user = models.ForeignKey("users.User",
                             on_delete=models.CASCADE,
                             related_name="workspace_member_sets")

    @classmethod
    def validate_members(cls, workspace_id: str, user_ids: Sequence[int]) -> Sequence[int]:
        """
        Validate member of workspace, if any user not in
        this workspace raises an Exception contains list invalid user_id.

        :param workspace_id: str
        :param user_ids: list<int>
        :return: list<int>
        """
        user_ids = set(user_ids)
        valid_members = cls.objects.filter(
            workspace_id=workspace_id,
            user_id__in=user_ids
        ).values_list("user", flat=True)

        diff = user_ids - set(valid_members)
        if diff:
            msg = str(valid_members)
            raise ValidationError(detail=msg)

        return list(valid_members)

    class Meta:
        index_together = [
            ["workspace", "user", "is_removed"]
        ]
        constraints = [
            UniqueConstraint(
                fields=["workspace", "user"],
                condition=Q(is_removed=False),
                name=UNIQUE_WORKSPACE_AND_USER_CONSTRAINT_NAME
            )
        ]

    def __str__(self):
        return f"User `{self.user_id}` of Workspace `{self.workspace_id}`"
