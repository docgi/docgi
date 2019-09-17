from django.db import models

from model_utils.models import TimeStampedModel, SoftDeletableModel


class Workspace(SoftDeletableModel, TimeStampedModel):
    name = models.CharField(unique=True,
                            primary_key=True,
                            max_length=128,
                            db_index=True)

    def __str__(self):
        return self.name
