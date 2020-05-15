import uuid

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

User = get_user_model()


class DocgiActivity(models.Model):
    id = models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True)

    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="activities",
    )
    verb = models.TextField()
    target_id = models.CharField(max_length=150)
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_content = GenericForeignKey("target_content_type", "target_id")
    at = models.DateTimeField(auto_now=True)

    workspace = models.ForeignKey(
        "workspaces.Workspace",
        on_delete=models.CASCADE,
        related_name="activities"
    )

    def __str__(self):
        return "action"
