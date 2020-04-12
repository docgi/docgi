import uuid as uuid
from os import path
from typing import Sequence

from django.conf import settings as app_settings, settings
from django.contrib.auth import get_user_model
from django.core.files.storage import get_storage_class
from django.db import models
from django.db.models import UniqueConstraint, Q
from django.utils.timezone import timedelta, now
from imagekit.models import ProcessedImageField
from model_utils.models import TimeStampedModel, SoftDeletableModel
from pilkit.processors import ResizeToFill
from rest_framework.exceptions import ValidationError

from docgi.base.models import Choices

User = get_user_model()
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
                            db_index=True,
                            editable=False)
    logo = ProcessedImageField(upload_to=logo_path,
                               storage=storage,
                               processors=[ResizeToFill(
                                   width=settings.WORKSPACE_LOGO_THUMBNAIL_WIDTH,
                                   height=settings.WORKSPACE_LOGO_THUMBNAIL_HEIGHT
                               )],
                               format="JPEG",
                               options={"quality": 90},
                               blank=True)

    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name="own_workspaces")

    def __str__(self):
        return self.name


class WorkspaceMember(SoftDeletableModel, TimeStampedModel):
    class WorkspaceMemberRole(Choices):
        ADMIN = 1
        MEMBER = 2

    workspace = models.ForeignKey(Workspace,
                                  on_delete=models.CASCADE,
                                  related_name="members")
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="workspace_member_sets")
    role = models.PositiveSmallIntegerField(choices=WorkspaceMemberRole.to_choices(),
                                            default=WorkspaceMemberRole.MEMBER.value)

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
            raise ValidationError("You have invited member not in this workspace.")

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
        return f"User {self.user_id} of Workspace {self.workspace_id}"


class Invitation(TimeStampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=10)
    email = models.EmailField()

    activate = models.BooleanField(default=True, db_index=True)

    workspace = models.ForeignKey("workspaces.Workspace",
                                  on_delete=models.CASCADE)
    workspace_role = models.PositiveSmallIntegerField(choices=WorkspaceMember.WorkspaceMemberRole.to_choices(),
                                                      default=WorkspaceMember.WorkspaceMemberRole.MEMBER.value)

    inviter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def is_expire(self):
        expire_time = self.created + timedelta(seconds=app_settings.INVITATION_EXPIRE_DURING)
        current_time = now()
        return current_time > expire_time

    class Meta:
        unique_together = (
            ("email", "workspace")
        )

    def __str__(self):
        return f"Invitation {self.email} to {self.workspace_id}"
