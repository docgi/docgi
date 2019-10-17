from enum import Enum

from django.db.models import Manager
from django.db.models.signals import post_save


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
