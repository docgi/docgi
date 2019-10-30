from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth import get_user_model
from model_utils.models import TimeStampedModel

User = get_user_model()


class Collection(TimeStampedModel):
    workspace = models.ForeignKey("workspaces.Workspace",
                                  on_delete=models.CASCADE,
                                  related_name="collections")

    name = models.CharField(max_length=150)
    private = models.BooleanField(default=False)

    creator = models.ForeignKey(User,
                                on_delete=models.SET_NULL,
                                null=True,
                                related_name="owner_collections")
    members = models.ManyToManyField(User)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (
            ("workspace", "name"),
        )


class Document(TimeStampedModel):
    title = models.TextField()
    contents = models.TextField(blank=True)

    archive = models.BooleanField(default=False)
    draft = models.BooleanField(default=True)

    contributors = ArrayField(base_field=models.IntegerField())

    class Meta:
        ordering = ("created",)

    def __str__(self):
        return self.title


class UserStarDoc(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="stared_docs")
    doc = models.ForeignKey(Document,
                            on_delete=models.CASCADE,
                            related_name="star_users")

    def __str__(self):
        return f"User @{self.user_id} stared on Docs @{self.doc_id}"

    class Meta:
        unique_together = (
            ("user", "doc")
        )
