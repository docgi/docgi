import uuid
from os import path

from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.files.storage import get_storage_class
from django.db import models
from model_utils.models import TimeStampedModel

from docgi.base.models import ColorField

User = get_user_model()
storage = get_storage_class()()


class Collection(TimeStampedModel):
    id = models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True)

    name = models.CharField(max_length=150)
    private = models.BooleanField(default=False)
    emoji = models.CharField(max_length=10, blank=True)
    color = ColorField()

    creator = models.ForeignKey(User,
                                on_delete=models.SET_NULL,
                                null=True,
                                related_name="owner_collections")
    workspace = models.ForeignKey("workspaces.Workspace",
                                  on_delete=models.CASCADE,
                                  related_name="collections")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("name",)


class Document(TimeStampedModel):
    id = models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True)

    name = models.CharField(max_length=512)
    html_content = models.TextField(blank=True)
    json_content = JSONField(default=list, null=True, blank=True)

    archive = models.BooleanField(default=False)
    draft = models.BooleanField(default=False)

    collection = models.ForeignKey(Collection,
                                   on_delete=models.CASCADE,
                                   related_name="documents")
    creator = models.ForeignKey(User,
                                null=True,
                                on_delete=models.SET_NULL,
                                related_name="owner_docs")
    contributors = models.ManyToManyField(User,
                                          related_name="contributed_docs")

    class Meta:
        ordering = ("created",)

    def __str__(self):
        return self.name


class DocumentImage(models.Model):
    def image_path(self, filename, *args, **kwargs):
        paths = [
            settings.DOCUMENT_IMAGE_DIR,
            str(uuid.uuid4()),
            path.basename(filename)
        ]
        return path.join(*paths)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey("workspaces.Workspace", on_delete=models.CASCADE, related_name="+")
    image = models.ImageField(
        storage=storage,
        upload_to=image_path
    )
