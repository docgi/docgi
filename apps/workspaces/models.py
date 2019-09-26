from os import path

from django.conf import settings as app_settings
from django.core.files.storage import get_storage_class
from django.db import models

from model_utils.models import TimeStampedModel, SoftDeletableModel

storage = get_storage_class()()


class Workspace(SoftDeletableModel, TimeStampedModel):
    def logo_path(self, filename, *args, **kwargs):
        paths = [
            app_settings.WORKSPACE_LOGO_DIR_NAME,
            str(self.name),
            path.basename(filename)
        ]
        return path.join(*paths)

    name = models.CharField(unique=True,
                            primary_key=True,
                            max_length=128,
                            db_index=True)
    logo = models.FileField(storage=storage,
                            upload_to=logo_path,
                            null=True,
                            blank=True)

    def __str__(self):
        return self.name
