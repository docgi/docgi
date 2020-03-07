from enum import Enum

from django.core.validators import MinLengthValidator
from django.db.models import Manager, CharField
from django.db.models.signals import post_save

DEFAULT_COLOR = "cdd7d6"
MAX_LENGTH_COLOR = 6


class Choices(Enum):
    @classmethod
    def to_choices(cls):
        # Find duplicate value, if any raise exception.
        values = cls.__members__.values()
        seen = set(values)
        if len(seen) < len(values):
            raise Exception(f"{cls.name} has duplicate values.")

        return [
            (item[1].value, item[1].name.replace("_", " ").title())
            for item in cls.__members__.items()
        ]


class BulkCreateModelManager(Manager):
    def bulk_create(self, objs, **kwargs):
        instances = super().bulk_create(objs=objs, **kwargs)
        for instance in instances:
            post_save.send(sender=self.model, instance=instance, created=True)
        return instances


class ColorField(CharField):
    def __init__(self, **kwargs):
        kwargs.update(
            null=True,
            blank=True,
            default=DEFAULT_COLOR,
            max_length=MAX_LENGTH_COLOR
        )
        super().__init__(**kwargs)
        self.validators.append(MinLengthValidator(6))
