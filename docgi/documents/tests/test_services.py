from factory.django import DjangoModelFactory

from .. import models


class CollectionFactory(DjangoModelFactory):
    class Meta:
        model = models.Collection
