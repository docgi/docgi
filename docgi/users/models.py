from os import path

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import get_storage_class
from django.db import models
from django.utils.functional import cached_property
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from docgi.utils import strings

storage = get_storage_class()()


class User(AbstractUser):
    def avatar_path(self, filename, *args, **kwargs):
        paths = [
            settings.USER_AVATAR_DIRNAME,
            str(self.pk),
            path.basename(filename)
        ]
        return path.join(*paths)

    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    avatar = ProcessedImageField(upload_to=avatar_path,
                                 storage=storage,
                                 processors=[ResizeToFill(
                                     width=settings.AVATAR_THUMBNAIL_WIDTH,
                                     height=settings.AVATAR_THUMBNAIL_HEIGHT
                                 )],
                                 format="JPEG",
                                 options={"quality": 90},
                                 blank=True)

    def get_jwt_current_workspace_name(self):
        from docgi.auth.jwt import KEY_USER_WORKSPACE_NAME
        return getattr(self, KEY_USER_WORKSPACE_NAME, None)

    def get_jwt_current_workspace_role(self):
        from docgi.auth.jwt import KEY_USER_WORKSPACE_ROLE
        return getattr(self, KEY_USER_WORKSPACE_ROLE, None)

    @cached_property
    def current_workspace(self):
        from docgi.auth.jwt import KEY_USER_WORKSPACE_NAME
        from docgi.workspaces.models import Workspace

        current_workspace_name = getattr(self, KEY_USER_WORKSPACE_NAME, None)
        workspace = Workspace.objects.get(
            name=current_workspace_name
        )
        return workspace

    @cached_property
    def current_workspace_member(self):
        from docgi.workspaces.models import WorkspaceMember
        from docgi.auth.jwt import KEY_USER_WORKSPACE_NAME

        current_workspace_name = getattr(self, KEY_USER_WORKSPACE_NAME, None)
        member = WorkspaceMember.objects.get(
            user=self,
            workspace_id__iexact=current_workspace_name
        )
        return member

    @classmethod
    def get_or_create(cls, email: str):
        email = email.lower()
        try:
            user = cls.objects.get(email__iexact=email)
        except cls.DoesNotExist:
            username = email[:email.find("@")]

            while cls.objects.filter(username__iexact=username).exists():
                username = strings.gen_username(email=email)

            user = cls.objects.create(
                email=email, username=username
            )
            user.set_unusable_password()
            user.save()
        return user

    def __str__(self):
        return self.username or self.email
